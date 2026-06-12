from django.conf import settings
from django.contrib.auth import views as auth_views
from django.core.cache import cache
from django.shortcuts import redirect

from .forms import LoginForm

_MAX_ATTEMPTS = getattr(settings, 'AUTH_MAX_FAILED_ATTEMPTS', 5)
_LOCKOUT_TTL = getattr(settings, 'AUTH_LOCKOUT_DURATION', 300)
_SESSION_REMEMBER_AGE = getattr(settings, 'AUTH_SESSION_REMEMBER_AGE', 60 * 60 * 24 * 30)


def _client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR', '127.0.0.1')


def _fail_key(ip):
    return f'auth:fail:{ip}'


class LoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST' and cache.get(_fail_key(_client_ip(request)), 0) >= _MAX_ATTEMPTS:
            form = self.get_form_class()(request)
            return self.render_to_response(self.get_context_data(form=form))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ip = _client_ip(self.request)
        attempts = cache.get(_fail_key(ip), 0)
        ctx['bloqueado'] = attempts >= _MAX_ATTEMPTS
        ctx['tentativas_restantes'] = max(0, _MAX_ATTEMPTS - attempts)
        ctx['lockout_minutos'] = _LOCKOUT_TTL // 60
        return ctx

    def form_invalid(self, form):
        ip = _client_ip(self.request)
        key = _fail_key(ip)
        attempts = cache.get(key, 0) + 1
        cache.set(key, attempts, _LOCKOUT_TTL)
        return super().form_invalid(form)

    def form_valid(self, form):
        ip = _client_ip(self.request)
        cache.delete(_fail_key(ip))
        if form.cleaned_data.get('remember_me'):
            self.request.session.set_expiry(_SESSION_REMEMBER_AGE)
        else:
            self.request.session.set_expiry(0)
        return super().form_valid(form)


class LogoutView(auth_views.LogoutView):
    pass


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'registration/password_change_form.html'


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = 'registration/password_change_done.html'


class PasswordResetView(auth_views.PasswordResetView):
    template_name = 'registration/password_reset_form.html'


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'
