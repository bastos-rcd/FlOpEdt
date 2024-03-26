from django import forms
from django.core.files.storage import FileSystemStorage

fs = FileSystemStorage()


class fileform(forms.Form):
    file = forms.FileField()
