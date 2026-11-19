from django import forms

from .models import Equipo


class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ("nombre", "ciudad", "nivel", "descripcion", "foto")
        labels = {"nombre": "Nombre del equipo", "ciudad": "Ciudad", "nivel": "Nivel", "descripcion": "Descripción", "foto": "Fotografía del equipo"}
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 3, "placeholder": "¿Qué tipo de parche son?"}), "foto": forms.FileInput(attrs={"accept": "image/jpeg,image/png,image/webp"})}

    def clean_foto(self):
        foto = self.cleaned_data.get("foto")
        if foto and foto.size > 5 * 1024 * 1024:
            raise forms.ValidationError("La fotografía no puede superar 5 MB.")
        if foto and getattr(foto, "content_type", "") not in {"image/jpeg", "image/png", "image/webp"}:
            raise forms.ValidationError("Usa una imagen JPG, PNG o WEBP.")
        return foto
