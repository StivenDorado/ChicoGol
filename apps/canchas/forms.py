from django import forms

from .models import Cancha, ResenaCancha


class CanchaFiltroForm(forms.Form):
    q = forms.CharField(label="Buscar", required=False)
    modalidad = forms.ChoiceField(label="Modalidad", required=False, choices=[("", "Todas las modalidades"), *Cancha.MODALIDAD_CHOICES])


CIUDAD_CHOICES = [
    ("Popayán", "Popayán"),
    ("Bogotá", "Bogotá"),
    ("Cali", "Cali"),
    ("Medellín", "Medellín"),
    ("Pasto", "Pasto"),
    ("Neiva", "Neiva"),
    ("Armenia", "Armenia"),
    ("Manizales", "Manizales"),
    ("Pereira", "Pereira"),
    ("Cartagena", "Cartagena"),
    ("Barranquilla", "Barranquilla"),
    ("Bucaramanga", "Bucaramanga"),
    ("Santa Marta", "Santa Marta"),
]

BARRIOS_POPAYAN = (
    "Bolívar", "Centro", "El Cadillal", "El Recuerdo", "La Esmeralda",
    "La Paz", "Las Américas", "Los Hoyos", "Prados del Norte", "Santa Clara",
    "Valencia",
)


class CanchaForm(forms.ModelForm):
    ciudad = forms.ChoiceField(label="Ciudad", choices=CIUDAD_CHOICES)

    class Meta:
        model = Cancha
        fields = (
            "nombre", "foto", "direccion", "ciudad", "barrio", "precio_hora",
            "tipo", "modalidad", "servicios", "descripcion", "latitud", "longitud",
        )
        labels = {
            "nombre": "Nombre de la cancha",
            "foto": "Fotografía",
            "direccion": "Dirección",
            "barrio": "Barrio o zona",
            "precio_hora": "Precio por hora",
            "tipo": "Tipo de superficie",
            "modalidad": "Modalidad",
            "servicios": "Servicios",
            "descripcion": "Descripción",
            "latitud": "Latitud",
            "longitud": "Longitud",
        }
        widgets = {
            "foto": forms.FileInput(attrs={"accept": "image/jpeg,image/png,image/webp", "data-court-photo": "true"}),
            "barrio": forms.TextInput(attrs={"placeholder": "Ej. Centro", "data-barrio-input": "true"}),
            "precio_hora": forms.NumberInput(attrs={"min": 0, "step": 1000, "placeholder": "0"}),
            "servicios": forms.TextInput(attrs={"placeholder": "Duchas, parqueadero, iluminación"}),
            "descripcion": forms.Textarea(attrs={"rows": 3, "placeholder": "Cuéntale a la comunidad qué hace especial esta cancha"}),
            "latitud": forms.HiddenInput(),
            "longitud": forms.HiddenInput(),
        }

    def clean_foto(self):
        foto = self.cleaned_data.get("foto")
        if foto:
            if foto.size > 3 * 1024 * 1024:
                raise forms.ValidationError("La fotografía no puede superar 3 MB.")
            content_type = getattr(foto, "content_type", "")
            if content_type and content_type not in {"image/jpeg", "image/png", "image/webp"}:
                raise forms.ValidationError("Usa una imagen JPG, PNG o WebP.")
        return foto

    def clean_barrio(self):
        barrio = self.cleaned_data.get("barrio", "").strip()
        ciudad = self.cleaned_data.get("ciudad")
        if not barrio:
            raise forms.ValidationError("Indica el barrio o la zona.")
        if ciudad == "Popayán" and barrio not in BARRIOS_POPAYAN:
            raise forms.ValidationError("Selecciona un barrio válido de Popayán.")
        return barrio

    def clean(self):
        cleaned = super().clean()
        latitud = cleaned.get("latitud")
        longitud = cleaned.get("longitud")
        if latitud is None or longitud is None:
            raise forms.ValidationError("Selecciona la ubicación exacta en el mapa.")
        if not (-90 <= latitud <= 90 and -180 <= longitud <= 180):
            raise forms.ValidationError("Las coordenadas de la cancha no son válidas.")
        return cleaned


class ResenaCanchaForm(forms.ModelForm):
    class Meta:
        model = ResenaCancha
        fields = ("calificacion", "comentario")
        labels = {"calificacion": "Calificación", "comentario": "Tu comentario"}
        widgets = {
            "calificacion": forms.Select(choices=[(5, "5 estrellas"), (4, "4 estrellas"), (3, "3 estrellas"), (2, "2 estrellas"), (1, "1 estrella")]),
            "comentario": forms.Textarea(attrs={"rows": 4, "maxlength": 600, "placeholder": "¿Qué tal fue jugar aquí?"}),
        }
