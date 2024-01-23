from django import forms
import re
from django.core.exceptions import ValidationError
from .models import Plataforma, Desarrolladores, Genero


def validar_fecha(value):
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', value):
        raise ValidationError(
            'El Formato de fecha incorrecto, debe ser YYYY-MM-DD')


class FechaLanzamientoForm(forms.Form):
    fecha = forms.CharField(label='Fecha de lanzamiento',
                            validators=[validar_fecha])


class NombrePlataformaChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.nombre


class PlataformasForm(forms.Form):
    plataforma = NombrePlataformaChoiceField(
        queryset=Plataforma.objects.all(), label='Selecciona una plataforma')


class DesarrolladorDescripcionForm(forms.Form):
    desarrollador = forms.ModelChoiceField(queryset=Desarrolladores.objects.all(
    ), label='Selecciona un desarrollador', required=False)
    busqueda = forms.CharField(label='Introduce las palabras a buscar', max_length=100, min_length=1,
                               widget=forms.TextInput, required=False)


class GeneroNombreForm(forms.Form):
    generos = forms.ModelChoiceField(
        queryset=Genero.objects.all(), label='Selecciona un género')
    busqueda = forms.CharField(label='Introduce un nombre a buscar', max_length=100, min_length=1,
                               widget=forms.TextInput)


def validate_email(value):
    if not re.match(r'^\w+([.-]?\w+)*@(gmail|hotmail|outlook).com$', value):
        raise ValidationError(
            'el email debe de ser de gmail, hotmail o outlook')


class RegisterForm(forms.Form):
    username = forms.CharField(
        label='Nombre de usuario',
        max_length=100,
        min_length=6,
        widget=forms.TextInput,
        required=True
    )
    email = forms.EmailField(
        label='Correo electrónico',
        max_length=100,
        widget=forms.EmailInput,
        required=True,
        validators=[validate_email]
    )
    password = forms.CharField(
        label='Contraseña',
        max_length=100,
        min_length=6,
        widget=forms.PasswordInput,
        required=True
    )
    first_name = forms.CharField(
        label='Nombre',
        max_length=100,
        min_length=3,
        widget=forms.TextInput,
        required=True
    )
    last_name = forms.CharField(
        label='Apellidos',
        max_length=100,
        min_length=3,
        widget=forms.TextInput,
        required=True
    )


class LoginForm(forms.Form):
    username = forms.CharField(label='Nombre de usuario', max_length=100,
                               min_length=6, widget=forms.TextInput, required=True)
    password = forms.CharField(label='Contraseña', max_length=100, min_length=6,
                               widget=forms.PasswordInput, required=True)

class VideoJuegoForm(forms.Form):
    nombre_videojuego = forms.CharField(label='Nombre del videojuego', max_length=100,
                               min_length=1, widget=forms.TextInput, required=True)
