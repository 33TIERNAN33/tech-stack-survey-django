from django.contrib import admin
from django.utils.html import format_html

from .models import Donor, Item, ItemRequest, Survivor, UserProfile


admin.site.site_header = "CareTrack Admin"
admin.site.site_title = "CareTrack Admin"
admin.site.index_title = "Operations Dashboard"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "email", "role", "approval_badge")
    list_filter = ("role", "is_approved")
    search_fields = ("user__username", "user__email")
    list_select_related = ("user",)
    list_per_page = 25
    fieldsets = (
        ("Account", {"fields": ("user",)}),
        ("Access", {"fields": ("role", "is_approved")}),
    )

    @admin.display(description="Email", ordering="user__email")
    def email(self, obj):
        return obj.user.email or "No email"

    @admin.display(description="Approval", ordering="is_approved")
    def approval_badge(self, obj):
        label = "Approved" if obj.is_approved else "Pending"
        class_name = "admin-badge admin-badge-success" if obj.is_approved else "admin-badge admin-badge-warning"
        return format_html('<span class="{}">{}</span>', class_name, label)


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ("display_name", "email", "phone", "anonymous_badge", "item_count")
    list_filter = ("anonymous",)
    search_fields = ("name", "email", "phone")
    list_per_page = 25
    fieldsets = (
        ("Donor Details", {"fields": ("name", "anonymous")}),
        ("Contact", {"fields": ("email", "phone")}),
    )

    @admin.display(description="Donor", ordering="name")
    def display_name(self, obj):
        return str(obj)

    @admin.display(description="Privacy", ordering="anonymous")
    def anonymous_badge(self, obj):
        if obj.anonymous:
            return format_html('<span class="{}">{}</span>', "admin-badge admin-badge-muted", "Anonymous")
        return format_html('<span class="{}">{}</span>', "admin-badge admin-badge-success", "Named")

    @admin.display(description="Items")
    def item_count(self, obj):
        return obj.items.count()


@admin.register(Survivor)
class SurvivorAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_summary", "assigned_item_count")
    search_fields = ("name", "contact_info")
    list_per_page = 25
    fieldsets = (
        ("Survivor", {"fields": ("name",)}),
        ("Contact Notes", {"fields": ("contact_info",)}),
    )

    @admin.display(description="Contact")
    def contact_summary(self, obj):
        return obj.contact_info or "No contact info"

    @admin.display(description="Assigned Items")
    def assigned_item_count(self, obj):
        return obj.assigned_items.count()


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category_label",
        "status_badge",
        "storage_location",
        "donor",
        "assigned_to",
        "created_date",
    )
    list_filter = ("status", "category")
    search_fields = ("name", "description", "category", "storage_location", "donor__name", "assigned_to__name")
    list_select_related = ("donor", "assigned_to")
    date_hierarchy = "created_date"
    list_per_page = 25
    fieldsets = (
        ("Item Details", {"fields": ("name", "description", "category", "image_path")}),
        ("Inventory Status", {"fields": ("status", "storage_location")}),
        ("People", {"fields": ("donor", "assigned_to")}),
    )

    @admin.display(description="Category", ordering="category")
    def category_label(self, obj):
        return obj.category or "Uncategorized"

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        if obj.status == Item.Status.AVAILABLE:
            return format_html('<span class="{}">{}</span>', "admin-badge admin-badge-success", "Available")
        return format_html('<span class="{}">{}</span>', "admin-badge admin-badge-info", "Distributed")


@admin.register(ItemRequest)
class ItemRequestAdmin(admin.ModelAdmin):
    list_display = ("item", "requester", "status_badge", "request_date")
    list_filter = ("status",)
    search_fields = ("item__name", "requester__username", "requester__email")
    list_select_related = ("item", "requester")
    date_hierarchy = "request_date"
    list_per_page = 25
    fieldsets = (
        ("Request", {"fields": ("item", "requester")}),
        ("Review", {"fields": ("status",)}),
    )

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        styles = {
            ItemRequest.Status.PENDING: ("admin-badge admin-badge-warning", "Pending"),
            ItemRequest.Status.APPROVED: ("admin-badge admin-badge-success", "Approved"),
            ItemRequest.Status.DENIED: ("admin-badge admin-badge-danger", "Denied"),
        }
        class_name, label = styles[obj.status]
        return format_html('<span class="{}">{}</span>', class_name, label)
