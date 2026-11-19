from datetime import date

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Perfil


def calcular_edad(fecha, hoy=None):
    hoy = hoy or date.today()
    return hoy.year - fecha.year - ((hoy.month, hoy.day) < (fecha.month, fecha.day))


def fecha_maxima_para_13(hoy=None):
    hoy = hoy or date.today()
    try:
        return hoy.replace(year=hoy.year - 13)
    except ValueError:
        return hoy.replace(year=hoy.year - 13, day=28)


class RegistroForm(UserCreationForm):
    email = forms.EmailField(label="Correo electrónico", required=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "password1", "password2")
        labels = {"first_name": "Nombre", "last_name": "Apellido", "username": "Nombre de usuario"}
        help_texts = {"username": "Usa letras, números y @/./+/-/_ únicamente."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fecha_nacimiento"] = forms.DateField(
            label="Fecha de nacimiento",
            required=True,
            help_text="Debes tener mínimo 13 años para crear tu cuenta.",
            widget=forms.DateInput(attrs={"type": "date", "autocomplete": "bday", "max": fecha_maxima_para_13().isoformat()}),
        )

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo.")
        return email

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data["fecha_nacimiento"]
        edad = calcular_edad(fecha)
        if edad < 13:
            raise forms.ValidationError("Debes tener mínimo 13 años para registrarte en ChicoGol.")
        if edad > 100:
            raise forms.ValidationError("Revisa la fecha de nacimiento.")
        return fecha


class InicioSesionForm(AuthenticationForm):
    username = forms.CharField(label="Usuario", widget=forms.TextInput(attrs={"autocomplete": "username"}))
    password = forms.CharField(label="Contraseña", strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}))


class PerfilForm(forms.ModelForm):
    CIUDADES_COLOMBIA = (
        ("Popayán", "Popayán · Cauca"),
        ("Bogotá", "Bogotá D.C."),
        ("Cali", "Cali · Valle del Cauca"),
        ("Medellín", "Medellín · Antioquia"),
        ("Pasto", "Pasto · Nariño"),
        ("Neiva", "Neiva · Huila"),
        ("Armenia", "Armenia · Quindío"),
        ("Manizales", "Manizales · Caldas"),
        ("Pereira", "Pereira · Risaralda"),
        ("Cartagena", "Cartagena · Bolívar"),
        ("Barranquilla", "Barranquilla · Atlántico"),
        ("Bucaramanga", "Bucaramanga · Santander"),
        ("Santa Marta", "Santa Marta · Magdalena"),
    )
    BARRIOS_POPAYAN = (
        "Alfonso López", "Bello Horizonte", "Centro", "Ciudad Jardín", "El Recuerdo",
        "La Esmeralda", "Las Ferias", "Loma de Cartagena", "Los Hoyos", "Morinda",
        "Pandiguando", "Santa Clara", "Valencia", "Villa del Norte",
    )

    class Meta:
        model = Perfil
        fields = ("ciudad", "barrio", "fecha_nacimiento", "telefono", "posicion", "nivel", "bio", "avatar")
        labels = {"ciudad": "Ciudad", "barrio": "Barrio o zona", "fecha_nacimiento": "Fecha de nacimiento", "telefono": "Teléfono", "posicion": "Posición", "nivel": "Nivel de juego", "bio": "Sobre tu juego", "avatar": "Fotografía de perfil"}
        widgets = {
            "ciudad": forms.Select(),
            "barrio": forms.TextInput(attrs={"data-barrio-input": "true", "placeholder": "Escribe tu barrio o zona"}),
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date", "autocomplete": "bday"}),
            "bio": forms.Textarea(attrs={"rows": 3, "placeholder": "Cuéntale algo a tu próximo equipo"}),
            "avatar": forms.FileInput(attrs={"accept": "image/jpeg,image/png,image/webp", "class": "profile-avatar-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ciudad"].choices = (("", "Selecciona una ciudad"),) + self.CIUDADES_COLOMBIA
        self.fields["ciudad"].required = True
        self.fields["ciudad"].widget.attrs["data-city-select"] = "true"
        self.fields["fecha_nacimiento"].required = True
        self.fields["fecha_nacimiento"].help_text = "Debes tener mínimo 13 años para participar."
        self.fields["fecha_nacimiento"].widget.attrs["max"] = fecha_maxima_para_13().isoformat()
        if self.is_bound:
            ciudad = self.data.get(self.add_prefix("ciudad"), "")
        else:
            ciudad = self.instance.ciudad
        if ciudad == "Popayán":
            self.fields["barrio"].widget = forms.Select(choices=(("", "Selecciona un barrio"),) + tuple((barrio, barrio) for barrio in self.BARRIOS_POPAYAN), attrs={"data-barrio-select": "true"})

    def clean_ciudad(self):
        ciudad = self.cleaned_data.get("ciudad")
        if ciudad not in dict(self.CIUDADES_COLOMBIA):
            raise forms.ValidationError("Selecciona una ciudad de Colombia.")
        return ciudad

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get("fecha_nacimiento")
        if not fecha:
            return fecha
        edad = calcular_edad(fecha)
        if edad < 13:
            raise forms.ValidationError("Debes tener mínimo 13 años para usar ChicoGol.")
        if edad > 100:
            raise forms.ValidationError("Revisa la fecha de nacimiento.")
        return fecha

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("ciudad") == "Popayán" and cleaned.get("barrio") not in self.BARRIOS_POPAYAN:
            self.add_error("barrio", "Selecciona un barrio válido de Popayán.")
        if cleaned.get("fecha_nacimiento"):
            cleaned["edad"] = calcular_edad(cleaned["fecha_nacimiento"])
        return cleaned

    def save(self, commit=True):
        perfil = super().save(commit=False)
        perfil.edad = self.cleaned_data.get("edad")
        if commit:
            perfil.save()
        return perfil

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if avatar and avatar.size > 3 * 1024 * 1024:
            raise forms.ValidationError("La fotografía no puede superar 3 MB.")
        if avatar and getattr(avatar, "content_type", "") not in {"image/jpeg", "image/png", "image/webp"}:
            raise forms.ValidationError("Usa una imagen JPG, PNG o WebP.")
        return avatar


class DatosPersonalesForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        labels = {"first_name": "Nombres", "last_name": "Apellidos", "email": "Correo electrónico"}
