from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models


class UserProfile(models.Model):
    class Role(models.TextChoices):
        PUBLIC = "public", "Public"
        DONOR = "donor", "Donor"
        SURVIVOR = "survivor", "Survivor"
        VOLUNTEER = "volunteer", "Volunteer"
        STAFF = "staff", "Staff"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PUBLIC)
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ["user__username"]
        verbose_name = "user profile"
        verbose_name_plural = "user profiles"

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class Donor(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    anonymous = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        if self.anonymous:
            return f"Anonymous donor #{self.pk}"
        return self.name


class Survivor(models.Model):
    name = models.CharField(max_length=120)
    contact_info = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Item(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        DISTRIBUTED = "distributed", "Distributed"

    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=80, blank=True)
    storage_location = models.CharField(max_length=120, blank=True)
    image_path = models.FileField(
        upload_to="item_images/",
        max_length=255,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])],
    )
    donor = models.ForeignKey(
        Donor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="items",
    )
    assigned_to = models.ForeignKey(
        Survivor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_items",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name", "-created_date"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_date"]),
        ]

    def __str__(self):
        return self.name


class ItemRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        DENIED = "denied", "Denied"

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="item_requests",
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="requests",
    )
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    class Meta:
        ordering = ["-request_date"]
        indexes = [
            models.Index(fields=["requester"]),
            models.Index(fields=["item"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.requester} -> {self.item} ({self.get_status_display()})"
