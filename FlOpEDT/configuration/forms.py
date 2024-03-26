from django import forms
from django.core.validators import RegexValidator


DAYS = [
    ("m", "Monday"),
    ("tu", "Tuesday"),
    ("w", "Wenesday"),
    ("th", "Thursday"),
    ("f", "Friday"),
]

validator_time = RegexValidator(r"^\d{2}:\d{2}$", "Must be as 00:00")


class ImportFile(forms.Form):
    file = forms.FileField()


class ImportPlanif(forms.Form):
    fichier = forms.FileField()


class ImportConfig(forms.Form):
    # nom = forms.SlugField()
    # abbrev = forms.CharField(max_length=7)
    # day_start_time = forms.CharField(max_length=5, min_length=5, validators=[validator_time])
    # day_end_time = forms.CharField(max_length=5, min_length=5, validators=[validator_time])
    # lunch_start_time = forms.CharField(max_length=5, min_length=5, validators=[validator_time])
    # lunch_end_time = forms.CharField(max_length=5, min_length=5, validators=[validator_time])
    # days = forms.MultipleChoiceField(
    #     required=True,
    #     widget=forms.CheckboxSelectMultiple,
    #     choices=DAYS,
    # )
    fichier = forms.FileField()
