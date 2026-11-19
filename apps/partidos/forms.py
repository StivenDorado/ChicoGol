from django import forms
from django.utils import timezone

from apps.canchas.models import Cancha
from apps.equipos.models import Equipo

from .models import Partido


class PartidoForm(forms.ModelForm):
    cancha = forms.ModelChoiceField(
        label="Cancha disponible",
        queryset=Cancha.objects.none(),
        empty_label="Selecciona una cancha activa",
        help_text="Solo aparecen canchas activas registradas en ChicoGol.",
    )

    class Meta:
        model = Partido
        fields = ("equipo", "cancha", "fecha", "nivel", "descripcion")
        labels = {"equipo": "Equipo anfitrión", "cancha": "Cancha", "fecha": "Fecha y hora", "nivel": "Nivel", "descripcion": "Nota del partido"}
        widgets = {"fecha": forms.DateTimeInput(attrs={"type": "datetime-local"}), "descripcion": forms.Textarea(attrs={"rows": 3, "placeholder": "Ej. traer camiseta clara y llegar 15 min antes"})}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["equipo"].queryset = Equipo.objects.filter(miembros=user)
        self.fields["cancha"].queryset = Cancha.objects.filter(activa=True).order_by("ciudad", "nombre")

    def clean_fecha(self):
        fecha = self.cleaned_data["fecha"]
        if fecha <= timezone.now():
            raise forms.ValidationError("El partido debe programarse en una fecha futura.")
        return fecha


class PartidoFiltroForm(forms.Form):
    ciudad = forms.CharField(label="Ciudad", required=False)
    barrio = forms.CharField(label="Zona", required=False)
    fecha = forms.DateField(label="Fecha", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    nivel = forms.ChoiceField(label="Nivel", required=False, choices=[("", "Todos los niveles"), *Partido.NIVELES])
