from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import CareTrackAuthenticationForm, RegistrationForm
from .models import UserProfile


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


def available_inventory(request):
    return render(
        request,
        "hello/page_stub.html",
        {
            "page_title": "Available Inventory",
            "page_heading": "Available Inventory",
            "page_description": (
                "This page will list currently available donations with search, "
                "filtering, and pagination in a later checkpoint."
            ),
        },
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
    return render(
        request,
        "hello/page_stub.html",
        {
            "page_title": "Distributed Items",
            "page_heading": "Distributed Items",
            "page_description": (
                "This page is currently limited to approved staff members because "
                "it will contain survivor assignment history."
            ),
        },
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
                "Checkpoint 3 staff access is working. This dashboard is reserved "
                "for approved staff accounts."
            ),
        },
    )
