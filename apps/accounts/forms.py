from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'autocomplete': 'email',
            'placeholder': 'seu@email.com',
        }),
    )
    password = forms.CharField(
        label='Senha',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
        }),
    )
    remember_me = forms.BooleanField(
        required=False,
        label='Manter conectado por 30 dias',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.pop('autofocus', None)

    def get_invalid_login_error(self):
        return forms.ValidationError(
            'E-mail ou senha incorretos. Verifique seus dados e tente novamente.',
            code='invalid_login',
        )
