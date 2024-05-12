from dataclasses import dataclass
from typing import Union

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from taxi.models import Driver, Car


@dataclass
class LicenceNumberValidation:
    MAX_LENGTH: int = 8
    FIRST_CHARACTERS_RANGE: int = 3
    LAST_CHARACTERS_RANGE: int = 5


def driver_licence_validator(
    instance: Union["DriverLicenseUpdateForm", "DriverCreationForm"]
) -> str:

    license_number = instance.cleaned_data["license_number"]
    validator = LicenceNumberValidation

    if len(license_number) > validator.MAX_LENGTH:
        raise ValidationError(
            f"License number should be "
            f"less than {validator.MAX_LENGTH} symbols long"
        )

    if (
        not license_number[0:validator.FIRST_CHARACTERS_RANGE].isalpha()
        or not license_number[0:validator.FIRST_CHARACTERS_RANGE].isupper()
    ):
        raise ValidationError(
            f"First {validator.FIRST_CHARACTERS_RANGE} "
            f"characters of license number should be uppercase letters"
        )

    if not license_number[-validator.LAST_CHARACTERS_RANGE:].isdigit():
        raise ValidationError(
            f"Last {validator.LAST_CHARACTERS_RANGE} "
            f"characters of license number should be digits"
        )

    return license_number


class CarForm(forms.ModelForm):
    drivers = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Car
        fields = "__all__"


class DriverCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Driver
        fields = UserCreationForm.Meta.fields + (
            "first_name",
            "last_name",
            "license_number",
        )

    def clean_license_number(self):
        return driver_licence_validator(self)


class DriverLicenseUpdateForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ("license_number",)

    def clean_license_number(self):
        return driver_licence_validator(self)
