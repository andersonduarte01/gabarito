from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

INPUT    = 'input input-bordered w-full'
INPUT_PW = 'input input-bordered w-full'


def _aplicar_daisy(form_class, campos: dict):
    """Retorna uma subclasse do form com classes DaisyUI nos widgets informados."""
    class FormDaisy(form_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for nome, css in campos.items():
                if nome in self.fields:
                    self.fields[nome].widget.attrs.update({'class': css})
    return FormDaisy


LoginFormDaisy = _aplicar_daisy(AuthenticationForm, {
    'username': INPUT,
    'password': INPUT_PW,
})

PasswordChangeFormDaisy = _aplicar_daisy(PasswordChangeForm, {
    'old_password':  INPUT_PW,
    'new_password1': INPUT_PW,
    'new_password2': INPUT_PW,
})

PasswordResetFormDaisy = _aplicar_daisy(PasswordResetForm, {
    'email': INPUT,
})

SetPasswordFormDaisy = _aplicar_daisy(SetPasswordForm, {
    'new_password1': INPUT_PW,
    'new_password2': INPUT_PW,
})


class LoginView(auth_views.LoginView):
    authentication_form = LoginFormDaisy
    template_name = 'registration/login.html'
    redirect_authenticated_user = True  # redireciona quem já está logado


class PasswordChangeView(auth_views.PasswordChangeView):
    form_class = PasswordChangeFormDaisy
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('accounts:password_change_done')


class PasswordResetView(auth_views.PasswordResetView):
    form_class = PasswordResetFormDaisy
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    form_class = SetPasswordFormDaisy
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')
