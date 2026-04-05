from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Donor, Item, ItemRequest, UserProfile


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
        self.assertContains(response, "Checkpoint 3 staff access is working")


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
