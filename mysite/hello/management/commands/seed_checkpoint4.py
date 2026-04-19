from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from hello.models import Donor, Item, ItemRequest, Survivor, UserProfile


class Command(BaseCommand):
    help = "Seed example Checkpoint 4 donors, survivors, inventory, and item requests."

    def handle(self, *args, **options):
        donors = [
            self.get_donor("Maya Hernandez", "maya@example.com", "555-0101", False),
            self.get_donor("Northside Church", "donations@northside.example", "555-0102", False),
            self.get_donor("Anonymous Community Donor", "", "", True),
            self.get_donor("Elena Park", "elena@example.com", "555-0103", False),
            self.get_donor("Campus Supply Drive", "supplies@example.com", "555-0104", False),
        ]

        survivors = [
            self.get_survivor("Client A", "Staff contact only: shelter intake desk"),
            self.get_survivor("Client B", "Staff contact only: case manager referral"),
            self.get_survivor("Client C", "Staff contact only: phone on file"),
        ]

        item_data = [
            ("Winter Coat", "Warm adult winter coat, gently used", "Clothing", "Shelf A1", 0, None, Item.Status.AVAILABLE),
            ("Hygiene Kit", "Soap, toothbrush, toothpaste, shampoo", "Personal Care", "Shelf B2", 4, None, Item.Status.AVAILABLE),
            ("Canned Food Box", "Shelf-stable meals and canned vegetables", "Food", "Pantry Rack 1", 1, None, Item.Status.AVAILABLE),
            ("Twin Blanket", "Clean twin-size blanket", "Bedding", "Shelf C3", 2, None, Item.Status.AVAILABLE),
            ("Backpack", "Durable backpack for carrying supplies", "Bags", "Shelf A3", 3, None, Item.Status.AVAILABLE),
            ("Baby Diapers Pack", "Unopened size 3 diaper pack", "Child Care", "Shelf D1", 4, None, Item.Status.AVAILABLE),
            ("Transit Pass", "One local transit day pass", "Transportation", "Lockbox 1", 1, None, Item.Status.AVAILABLE),
            ("Phone Charger", "USB-C wall charger and cable", "Electronics", "Shelf E2", 3, None, Item.Status.AVAILABLE),
            ("Work Shoes", "Black non-slip work shoes, size 9", "Clothing", "Shelf A2", 0, 0, Item.Status.DISTRIBUTED),
            ("Grocery Gift Card", "Twenty-five dollar grocery card", "Food", "Lockbox 1", 2, 1, Item.Status.DISTRIBUTED),
            ("Towel Set", "Two bath towels and washcloths", "Bedding", "Shelf C1", 4, 2, Item.Status.DISTRIBUTED),
        ]

        items = []
        for name, description, category, location, donor_index, survivor_index, status in item_data:
            item, _ = Item.objects.update_or_create(
                name=name,
                defaults={
                    "description": description,
                    "category": category,
                    "storage_location": location,
                    "donor": donors[donor_index],
                    "assigned_to": survivors[survivor_index] if survivor_index is not None else None,
                    "status": status,
                },
            )
            items.append(item)

        requester = self.get_demo_requester()
        for item in items[:3]:
            ItemRequest.objects.get_or_create(
                requester=requester,
                item=item,
                defaults={"status": ItemRequest.Status.PENDING},
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {Donor.objects.count()} donors, "
                f"{Survivor.objects.count()} survivors, "
                f"{Item.objects.count()} items, and "
                f"{ItemRequest.objects.count()} item requests."
            )
        )

    def get_donor(self, name, email, phone, anonymous):
        donor, _ = Donor.objects.update_or_create(
            name=name,
            defaults={"email": email, "phone": phone, "anonymous": anonymous},
        )
        return donor

    def get_survivor(self, name, contact_info):
        survivor, _ = Survivor.objects.update_or_create(
            name=name,
            defaults={"contact_info": contact_info},
        )
        return survivor

    def get_demo_requester(self):
        User = get_user_model()
        requester, _ = User.objects.get_or_create(
            username="survivor_demo",
            defaults={"email": "survivor.demo@example.com"},
        )
        requester.set_password("StrongPassword123")
        requester.save()
        UserProfile.objects.update_or_create(
            user=requester,
            defaults={"role": UserProfile.Role.SURVIVOR, "is_approved": True},
        )
        return requester
