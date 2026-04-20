from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CareTrackAuthenticationForm, DonationForm, ItemForm, RegistrationForm
from .models import Item, UserProfile


def get_or_create_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            profile = get_or_create_profile(request.user)
            if profile.role not in allowed_roles or not profile.is_approved:
                return render(
                    request,
                    "hello/forbidden.html",
                    status=403,
                    context={
                        "page_title": "Access Restricted",
                        "page_heading": "Access Restricted",
                        "page_description": (
                            "Your account does not currently have permission to "
                            "view this page."
                        ),
                    },
                )
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def index(request):
    return render(request, "hello/index.html", {"login_form": CareTrackAuthenticationForm()})


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = get_or_create_profile(user)
            profile.role = form.cleaned_data["role"]
            profile.is_approved = profile.role == UserProfile.Role.DONOR
            profile.save()
            login(request, user)
            messages.success(request, "Your account has been created successfully.")
            return redirect("dashboard")
    else:
        form = RegistrationForm()

    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    profile = get_or_create_profile(request.user)
    return render(
        request,
        "hello/dashboard.html",
        {
            "profile": profile,
            "is_staff_role": profile.role == UserProfile.Role.STAFF and profile.is_approved,
        },
    )


def donate_item(request):
    if request.method == "POST":
        form = DonationForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save()
            messages.success(request, f"Donation submitted for {item.name}.")
            return redirect("available_inventory")
    else:
        form = DonationForm()

    return render(request, "hello/donation_form.html", {"form": form})


def filter_inventory_items(request, queryset):
    search_query = request.GET.get("q", "").strip()
    category_filter = request.GET.get("category", "").strip()
    status_filter = request.GET.get("status", "").strip()

    if search_query:
        queryset = queryset.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(category__icontains=search_query)
            | Q(storage_location__icontains=search_query)
        )

    if category_filter:
        queryset = queryset.filter(category__iexact=category_filter)

    if status_filter in Item.Status.values:
        queryset = queryset.filter(status=status_filter)

    return queryset, search_query, category_filter, status_filter


def paginate_items(request, queryset):
    paginator = Paginator(queryset, 5)
    return paginator.get_page(request.GET.get("page"))


def inventory_context(request, queryset, page_title, page_heading, **extra_context):
    filtered_items, search_query, category_filter, status_filter = filter_inventory_items(
        request,
        queryset,
    )
    page_obj = paginate_items(request, filtered_items)
    categories = (
        Item.objects.exclude(category="")
        .order_by("category")
        .values_list("category", flat=True)
        .distinct()
    )
    query_params = request.GET.copy()
    query_params.pop("page", None)
    is_approved_staff = False
    if request.user.is_authenticated:
        profile = get_or_create_profile(request.user)
        is_approved_staff = profile.role == UserProfile.Role.STAFF and profile.is_approved

    context = {
        "page_title": page_title,
        "page_heading": page_heading,
        "items": page_obj.object_list,
        "page_obj": page_obj,
        "search_query": search_query,
        "category_filter": category_filter,
        "status_filter": status_filter,
        "categories": categories,
        "status_choices": Item.Status.choices,
        "query_string": query_params.urlencode(),
        "is_approved_staff": is_approved_staff,
    }
    context.update(extra_context)
    return context


def available_inventory(request):
    items = Item.objects.select_related("donor", "assigned_to").order_by("-created_date")
    return render(
        request,
        "hello/inventory_list.html",
        inventory_context(
            request,
            items.filter(status=Item.Status.AVAILABLE),
            "Available Inventory",
            "Available Inventory",
            show_status_filter=False,
        ),
    )


def requested_items(request):
    return render(
        request,
        "hello/page_stub.html",
        {
            "page_title": "Requested Items",
            "page_heading": "Requested Items",
            "page_description": (
                "This page will highlight the items the organization currently "
                "needs so donors can respond."
            ),
        },
    )


@role_required(UserProfile.Role.STAFF)
def distributed_items(request):
    items = Item.objects.select_related("donor", "assigned_to").order_by("-created_date")
    return render(
        request,
        "hello/inventory_list.html",
        inventory_context(
            request,
            items.filter(status=Item.Status.DISTRIBUTED),
            "Distributed Items",
            "Distributed Items",
            show_survivor=True,
            show_status_filter=False,
        ),
    )


@role_required(UserProfile.Role.STAFF)
def staff_dashboard(request):
    return render(
        request,
        "hello/page_stub.html",
        {
            "page_title": "Staff Dashboard",
            "page_heading": "Staff Dashboard",
            "page_description": (
                "Checkpoint 4 CRUD access is working. This dashboard is reserved "
                "for approved staff accounts and links to inventory management."
            ),
        },
    )


@role_required(UserProfile.Role.STAFF)
def item_create(request):
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save()
            messages.success(request, f"{item.name} was added to inventory.")
            return redirect("available_inventory")
    else:
        form = ItemForm()

    return render(
        request,
        "hello/item_form.html",
        {"form": form, "page_title": "Add Inventory Item", "button_text": "Add Item"},
    )


@role_required(UserProfile.Role.STAFF)
def item_update(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            item = form.save()
            messages.success(request, f"{item.name} was updated.")
            return redirect("available_inventory")
    else:
        form = ItemForm(instance=item)

    return render(
        request,
        "hello/item_form.html",
        {"form": form, "item": item, "page_title": "Edit Inventory Item", "button_text": "Save Changes"},
    )


@role_required(UserProfile.Role.STAFF)
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == "POST":
        item_name = item.name
        item.delete()
        messages.success(request, f"{item_name} was removed from inventory.")
        return redirect("available_inventory")

    return render(request, "hello/item_confirm_delete.html", {"item": item})
