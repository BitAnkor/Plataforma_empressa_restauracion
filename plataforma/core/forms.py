from django import forms
from .models import Usuario
import secrets
import string

class UsuarioCreationForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('email', 'first_name', 'last_name', 'telefono', 'rol', 'local')

    def save(self, commit=True):
        user = super().save(commit=False)
        password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        user.set_password(password)
        self._generated_password = password

        if commit:
            user.save()
        return user

    def get_generated_password(self):
        return getattr(self, '_generated_password', None)



class PerfilUpdateForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['email', 'telefono']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border rounded-md', 'placeholder': 'Correo electrónico'}),
            'telefono': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md', 'placeholder': 'Número de teléfono'}),
        }
