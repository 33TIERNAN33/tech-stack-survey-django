import os
import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from .models import Donor, Item, ItemRequest, Survivor, UserProfile


class HomePageTests(TestCase):
    def test_home_page_renders_caretrack(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hello/index.html")
        self.assertContains(response, "Welcome to CareTrack")

    def test_home_page_uses_shared_navigation(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Available Inventory")
        self.assertContains(response, "Requested Items")
        self.assertContains(response, "Distributed Items")
        self.assertContains(response, "Login")
        self.assertContains(response, "Register")


class PageStructureTests(TestCase):
    def test_inventory_page_renders(self):
        response = self.client.get(reverse("available_inventory"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Available Inventory")

    def test_distributed_items_redirects_anonymous_users(self):
        response = self.client.get(reverse("distributed_items"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_staff_dashboard_forbids_non_staff_users(self):
        user = get_user_model().objects.create_user(
            username="volunteer1",
            email="volunteer@example.com",
            password="StrongPassword123",
        )
        UserProfile.objects.create(
            user=user,
            role=UserProfile.Role.VOLUNTEER,
            is_approved=True,
        )

        self.client.login(username="volunteer1", password="StrongPassword123")
        response = self.client.get(reverse("staff_dashboard"))

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Access Restricted", status_code=403)

    def test_staff_dashboard_allows_approved_staff(self):
        user = get_user_model().objects.create_user(
            username="staff1",
            email="staff@example.com",
            password="StrongPassword123",
        )
        UserProfile.objects.create(
            user=user,
            role=UserProfile.Role.STAFF,
            is_approved=True,
        )

        self.client.login(username="staff1", password="StrongPassword123")
        response = self.client.get(reverse("staff_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Checkpoint 4 CRUD access is working")


class AuthenticationFlowTests(TestCase):
    def test_registration_creates_user_and_profile(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "donor1",
                "email": "donor1@example.com",
                "role": UserProfile.Role.DONOR,
                "password1": "StrongPassword123",
                "password2": "StrongPassword123",
            },
        )

        self.assertRedirects(response, reverse("dashboard"))
        user = get_user_model().objects.get(username="donor1")
        self.assertEqual(user.profile.role, UserProfile.Role.DONOR)
        self.assertTrue(user.profile.is_approved)

    def test_login_page_authenticates_existing_user(self):
        get_user_model().objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="StrongPassword123",
        )

        response = self.client.post(
            reverse("login"),
            {"username": "existinguser", "password": "StrongPassword123"},
        )

        self.assertRedirects(response, reverse("dashboard"))
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "existinguser")


class CheckpointFourFeatureTests(TestCase):
    def create_staff_user(self):
        user = get_user_model().objects.create_user(
            username="staffcrud",
            email="staffcrud@example.com",
            password="StrongPassword123",
        )
        UserProfile.objects.create(
            user=user,
            role=UserProfile.Role.STAFF,
            is_approved=True,
        )
        return user

    def test_donation_form_creates_donor_and_item(self):
        response = self.client.post(
            reverse("donate_item"),
            {
                "donor_name": "Maya Helper",
                "donor_email": "maya@example.com",
                "donor_phone": "555-0100",
                "item_name": "Winter Coat",
                "description": "Warm adult-sized coat",
                "category": "Clothing",
            },
        )

        self.assertRedirects(response, reverse("available_inventory"))
        donor = Donor.objects.get(name="Maya Helper")
        item = Item.objects.get(name="Winter Coat")
        self.assertEqual(item.donor, donor)
        self.assertEqual(item.status, Item.Status.AVAILABLE)

    def test_inventory_page_displays_database_items(self):
        donor = Donor.objects.create(name="Local Donor")
        Item.objects.create(name="Canned Food Box", category="Food", donor=donor)

        response = self.client.get(reverse("available_inventory"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hello/inventory_list.html")
        self.assertContains(response, "Canned Food Box")
        self.assertContains(response, "Local Donor")

    def test_staff_can_create_update_and_delete_inventory_item(self):
        survivor = Survivor.objects.create(name="Client One")
        self.create_staff_user()
        self.client.login(username="staffcrud", password="StrongPassword123")

        create_response = self.client.post(
            reverse("item_create"),
            {
                "name": "Hygiene Kit",
                "description": "Soap and toothbrush",
                "category": "Personal Care",
                "storage_location": "Shelf A",
                "assigned_to": "",
                "donor": "",
                "status": Item.Status.AVAILABLE,
            },
        )
        self.assertRedirects(create_response, reverse("available_inventory"))
        item = Item.objects.get(name="Hygiene Kit")

        update_response = self.client.post(
            reverse("item_update", args=[item.pk]),
            {
                "name": "Updated Hygiene Kit",
                "description": "Soap, toothbrush, and shampoo",
                "category": "Personal Care",
                "storage_location": "Shelf B",
                "assigned_to": survivor.pk,
                "donor": "",
                "status": Item.Status.DISTRIBUTED,
            },
        )
        self.assertRedirects(update_response, reverse("available_inventory"))
        item.refresh_from_db()
        self.assertEqual(item.name, "Updated Hygiene Kit")
        self.assertEqual(item.status, Item.Status.DISTRIBUTED)
        self.assertEqual(item.assigned_to, survivor)

        delete_response = self.client.post(reverse("item_delete", args=[item.pk]))
        self.assertRedirects(delete_response, reverse("available_inventory"))
        self.assertFalse(Item.objects.filter(pk=item.pk).exists())

    def test_non_staff_cannot_access_item_create(self):
        user = get_user_model().objects.create_user(
            username="donorcrud",
            email="donorcrud@example.com",
            password="StrongPassword123",
        )
        UserProfile.objects.create(
            user=user,
            role=UserProfile.Role.DONOR,
            is_approved=True,
        )
        self.client.login(username="donorcrud", password="StrongPassword123")

        response = self.client.get(reverse("item_create"))

        self.assertEqual(response.status_code, 403)


class CheckpointFiveFeatureTests(TestCase):
    def setUp(self):
        self.temp_media = settings.BASE_DIR / "test_media"
        os.makedirs(self.temp_media / "item_images", exist_ok=True)
        self.media_override = override_settings(MEDIA_ROOT=self.temp_media)
        self.media_override.enable()
        self.addCleanup(self.media_override.disable)
        self.addCleanup(shutil.rmtree, self.temp_media, ignore_errors=True)

    def test_inventory_page_is_paginated(self):
        for index in range(7):
            Item.objects.create(name=f"Available Item {index}", category="Supplies")

        response = self.client.get(reverse("available_inventory"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["items"]), 5)
        self.assertContains(response, "Page 1 of 2")

        second_page = self.client.get(reverse("available_inventory"), {"page": 2})
        self.assertEqual(len(second_page.context["items"]), 2)

    def test_inventory_search_and_category_filter(self):
        Item.objects.create(name="Blue Winter Coat", category="Clothing")
        Item.objects.create(name="Shelf Stable Rice", category="Food")

        search_response = self.client.get(reverse("available_inventory"), {"q": "winter"})
        self.assertContains(search_response, "Blue Winter Coat")
        self.assertNotContains(search_response, "Shelf Stable Rice")

        filter_response = self.client.get(
            reverse("available_inventory"),
            {"category": "Food"},
        )
        self.assertContains(filter_response, "Shelf Stable Rice")
        self.assertNotContains(filter_response, "Blue Winter Coat")

    def test_donation_form_accepts_valid_image_upload(self):
        image = SimpleUploadedFile(
            "coat.png",
            b"\x89PNG\r\n\x1a\n" + b"checkpoint-five-image",
            content_type="image/png",
        )

        response = self.client.post(
            reverse("donate_item"),
            {
                "donor_name": "Image Donor",
                "donor_email": "image@example.com",
                "donor_phone": "555-0101",
                "item_name": "Photo Coat",
                "description": "Coat with uploaded image",
                "category": "Clothing",
                "image_path": image,
            },
        )

        self.assertRedirects(response, reverse("available_inventory"))
        item = Item.objects.get(name="Photo Coat")
        self.assertTrue(item.image_path.name.startswith("item_images/"))

    def test_donation_form_rejects_non_image_upload(self):
        upload = SimpleUploadedFile(
            "notes.txt",
            b"not an image",
            content_type="text/plain",
        )

        response = self.client.post(
            reverse("donate_item"),
            {
                "donor_name": "Bad Upload",
                "item_name": "Invalid Image Item",
                "category": "Clothing",
                "image_path": upload,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "image_path", "Only JPEG and PNG images can be uploaded.")
        self.assertFalse(Item.objects.filter(name="Invalid Image Item").exists())


class AdminPageTests(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="StrongPassword123",
        )
        self.client.force_login(self.admin_user)

    def test_donor_admin_changelist_renders(self):
        Donor.objects.create(name="Anonymous Helper", anonymous=True)
        Donor.objects.create(name="Named Helper", anonymous=False)

        response = self.client.get(reverse("admin:hello_donor_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Anonymous donor")
        self.assertContains(response, "Named Helper")

    def test_item_admin_changelist_renders(self):
        Item.objects.create(name="Available Coat", status=Item.Status.AVAILABLE)
        Item.objects.create(name="Distributed Kit", status=Item.Status.DISTRIBUTED)

        response = self.client.get(reverse("admin:hello_item_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Available Coat")
        self.assertContains(response, "Distributed Kit")


class ModelTests(TestCase):
    def test_item_request_defaults_to_pending(self):
        user = get_user_model().objects.create_user(
            username="survivor1",
            email="survivor@example.com",
            password="StrongPassword123",
        )
        donor = Donor.objects.create(name="Helpful Donor")
        item = Item.objects.create(name="Blanket", donor=donor)
        request = ItemRequest.objects.create(requester=user, item=item)

        self.assertEqual(request.status, ItemRequest.Status.PENDING)

    def test_user_profile_default_role_is_public(self):
        user = get_user_model().objects.create_user(
            username="newuser",
            email="newuser@example.com",
            password="StrongPassword123",
        )
        profile = UserProfile.objects.create(user=user)

        self.assertEqual(profile.role, UserProfile.Role.PUBLIC)
