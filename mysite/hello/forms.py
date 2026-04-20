from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Donor, Item, UserProfile


class CareTrackAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "autofocus": True})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    role = forms.ChoiceField(
        choices=[
            (UserProfile.Role.DONOR, "Donor"),
            (UserProfile.Role.SURVIVOR, "Survivor"),
            (UserProfile.Role.VOLUNTEER, "Volunteer"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control"})
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})


class DonationForm(forms.Form):
    MAX_IMAGE_SIZE = 2 * 1024 * 1024
    ALLOWED_IMAGE_SIGNATURES = {
        "jpg": (b"\xff\xd8\xff",),
        "jpeg": (b"\xff\xd8\xff",),
        "png": (b"\x89PNG\r\n\x1a\n",),
    }

    donor_name = forms.CharField(
        max_length=120,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    donor_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    donor_phone = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    anonymous = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    item_name = forms.CharField(
        max_length=120,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}),
    )
    category = forms.CharField(
        max_length=80,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    image_path = forms.FileField(
        label="Item Image",
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control"}),
    )

    def clean_image_path(self):
        image = self.cleaned_data.get("image_path")
        if not image:
            return image

        if image.size > self.MAX_IMAGE_SIZE:
            raise forms.ValidationError("Image uploads must be 2 MB or smaller.")

        extension = image.name.rsplit(".", 1)[-1].lower() if "." in image.name else ""
        signatures = self.ALLOWED_IMAGE_SIGNATURES.get(extension)
        if not signatures:
            raise forms.ValidationError("Only JPEG and PNG images can be uploaded.")

        header = image.read(16)
        image.seek(0)
        if not any(header.startswith(signature) for signature in signatures):
            raise forms.ValidationError("Uploaded image content must match JPEG or PNG format.")

        return image

    def save(self):
        donor = Donor.objects.create(
            name=self.cleaned_data["donor_name"],
            email=self.cleaned_data["donor_email"],
            phone=self.cleaned_data["donor_phone"],
            anonymous=self.cleaned_data["anonymous"],
        )
        return Item.objects.create(
            name=self.cleaned_data["item_name"],
            description=self.cleaned_data["description"],
            category=self.cleaned_data["category"],
            image_path=self.cleaned_data.get("image_path"),
            donor=donor,
        )


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = (
            "name",
            "description",
            "category",
            "storage_location",
            "image_path",
            "donor",
            "assigned_to",
            "status",
        )
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "category": forms.TextInput(attrs={"class": "form-control"}),
            "storage_location": forms.TextInput(attrs={"class": "form-control"}),
            "image_path": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "donor": forms.Select(attrs={"class": "form-select"}),
            "assigned_to": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_image_path(self):
        image = self.cleaned_data.get("image_path")
        if not image:
            return image

        if hasattr(image, "size") and image.size > DonationForm.MAX_IMAGE_SIZE:
            raise forms.ValidationError("Image uploads must be 2 MB or smaller.")

        if hasattr(image, "read"):
            extension = image.name.rsplit(".", 1)[-1].lower() if "." in image.name else ""
            signatures = DonationForm.ALLOWED_IMAGE_SIGNATURES.get(extension)
            if not signatures:
                raise forms.ValidationError("Only JPEG and PNG images can be uploaded.")

            header = image.read(16)
            image.seek(0)
            if not any(header.startswith(signature) for signature in signatures):
                raise forms.ValidationError("Uploaded image content must match JPEG or PNG format.")

        return image
