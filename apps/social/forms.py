from django import forms

from .models import Mensaje


class MensajeForm(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields = ("texto",)
        labels = {"texto": "Mensaje"}
        widgets = {"texto": forms.TextInput(attrs={"placeholder": "Escribe para tu equipo…", "autocomplete": "off"})}
