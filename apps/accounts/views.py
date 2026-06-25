from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

INPUT    = 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-sm placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-[#0d6efd] focus:border-transparent transition-colors'
INPUT_PW = 'w-full pl-3.5 pr-10 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-sm placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-[#0d6efd] focus:border-transparent transition-colors'


def _aplicar_classes(form_class, campos: dict):
    class FormComClasses(form_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for nome, css in campos.items():
                if nome in self.fields:
                    self.fields[nome].widget.attrs.update({'class': css})
    return FormComClasses


LoginFormDaisy = _aplicar_classes(AuthenticationForm, {
    'username': INPUT,
    'password': INPUT_PW,
})

PasswordChangeFormDaisy = _aplicar_classes(PasswordChangeForm, {
    'old_password':  INPUT_PW,
    'new_password1': INPUT_PW,
    'new_password2': INPUT_PW,
})

PasswordResetFormDaisy = _aplicar_classes(PasswordResetForm, {
    'email': INPUT,
})

SetPasswordFormDaisy = _aplicar_classes(SetPasswordForm, {
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
