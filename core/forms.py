from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import transaction

from .models import Mensaje, Cliente


class BootstrapMixin:
    """Agrega las clases de Bootstrap a todos los campos."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            w = campo.widget
            if isinstance(w, forms.CheckboxInput):
                clase = 'form-check-input'
            elif isinstance(w, (forms.Select, forms.SelectMultiple)):
                clase = 'form-select'
            else:
                clase = 'form-control'
            w.attrs['class'] = (w.attrs.get('class', '') + ' ' + clase).strip()


class LoginForm(BootstrapMixin, AuthenticationForm):
    pass


class RegistroForm(BootstrapMixin, UserCreationForm):
    first_name = forms.CharField(label='Nombre', max_length=150)
    last_name = forms.CharField(label='Apellido', max_length=150)
    email = forms.EmailField(label='Correo electrónico')
    telefono = forms.CharField(
        label='Teléfono', max_length=15,
        validators=[RegexValidator(r'^\d{7,15}$', 'Solo números, entre 7 y 15 dígitos.')])
    direccion = forms.CharField(label='Dirección', max_length=200)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con este correo.')
        return email

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.save()
        Cliente.objects.create(
            user=user,
            telefono=self.cleaned_data['telefono'],
            direccion=self.cleaned_data['direccion'],
        )
        return user


class MensajeForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Mensaje
        fields = ['nombre', 'email', 'asunto', 'mensaje']
        widgets = {'mensaje': forms.Textarea(attrs={'rows': 5})}