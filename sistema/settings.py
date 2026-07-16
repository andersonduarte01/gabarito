from pathlib import Path
from datetime import timedelta
import os
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, 'chave-dev-insegura'),
    ALLOWED_HOSTS=(list, ['educareprime.com.br', 'www.educareprime.com.br']),
)
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.inlines',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.forms',
    # Apps ativos
    'apps.core',
    'apps.accounts',
    'apps.escola',
    'apps.planos',        # Módulo 01
    'apps.onboarding',    # Módulo 02
    'apps.diretor',       # Módulo 07 (modelo PerfilDiretor necessário para M02)
    'apps.configuracao',   # Módulo 03
    'apps.notificacao',    # Módulo 04
    'apps.auditoria',      # Módulo 05
    'apps.ano_letivo',     # Módulo 11
    'apps.colaborador',    # Módulo 08
    'apps.professor',      # Módulo 09
    # Apps aguardando implementação (ativados conforme módulos forem implementados)
    # 'apps.professor',     # Módulo 09
    # 'apps.responsavel',   # Módulo 10
    # 'apps.ano_letivo',    # Módulo 11
    'apps.serie',         # Módulo 12
    'apps.turma',         # Módulo 13
    'apps.materia',       # Módulo 14
    'apps.responsavel',   # Módulo 10
    'apps.aluno',         # Módulo 15
    'apps.avaliacao',     # Módulo 16
    'apps.boletim',       # Módulo 17
    'apps.frequencia',    # Módulo 18
    # 'apps.boletim',       # Módulo 17
    # 'apps.frequencia',    # Módulo 18
    'apps.financeiro',    # Módulo 19
    'apps.comunicado',    # Módulo 20
    'apps.agenda',        # Módulo 20
    'apps.relatorio',     # Módulo 21
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.core.middleware.TenantMiddleware',
]

ROOT_URLCONF = 'sistema.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.notificacao.context_processors.notificacoes_counter',
                'apps.core.context_processors.base_template',
            ],
        },
    },
]

WSGI_APPLICATION = 'sistema.wsgi.application'

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True
DATE_INPUT_FORMATS = ['%d/%m/%Y']

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'core.Usuario'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# ── Segurança (Cloudflare Tunnel termina TLS) ────────────────────────────────
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False  # Cloudflare já termina TLS — redirecionar aqui causa loop
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

CSRF_TRUSTED_ORIGINS = [
    'https://educareprime.com.br',
    'https://www.educareprime.com.br',
]

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=3650),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=3650),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# ── E-mail ───────────────────────────────────────────────────────────────────
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.filebased.EmailBackend')
EMAIL_FILE_PATH = str(BASE_DIR / 'sent_emails')

# ── Django Unfold ─────────────────────────────────────────────────────────────
from django.urls import reverse_lazy

UNFOLD = {
    "SITE_TITLE":  "EduCare Admin",
    "SITE_HEADER": "EduCare",
    "SITE_URL":    "/",
    "SITE_SYMBOL": "school",
    "SHOW_HISTORY":      True,
    "SHOW_VIEW_ON_SITE": True,
    "COLORS": {
        "primary": {
            "50":  "239 246 255",
            "100": "219 234 254",
            "200": "191 219 254",
            "300": "147 197 253",
            "400": "96 165 250",
            "500": "59 130 246",
            "600": "13 110 253",
            "700": "11 94 215",
            "800": "30 64 175",
            "900": "30 58 138",
            "950": "23 37 84",
        },
    },
    "SIDEBAR": {
        "show_search":           True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Plataforma SaaS",
                "collapsible": False,
                "items": [
                    {"title": "Planos",      "icon": "deployed_code", "link": reverse_lazy("admin:planos_plano_changelist")},
                    {"title": "Assinaturas", "icon": "task_alt",      "link": reverse_lazy("admin:planos_assinaturaescola_changelist")},
                    {"title": "Módulos",     "icon": "extension",     "link": reverse_lazy("admin:planos_modulo_changelist")},
                ],
            },
            {
                "title": "Controle de Acesso",
                "collapsible": False,
                "items": [
                    {"title": "Usuários", "icon": "group",         "link": reverse_lazy("admin:core_usuario_changelist")},
                    {"title": "Vínculos", "icon": "swap_horiz",    "link": reverse_lazy("admin:core_vinculoescola_changelist")},
                    {"title": "Papéis",   "icon": "verified_user", "link": reverse_lazy("admin:core_papelvinculo_changelist")},
                ],
            },
            {
                "title": "Escolas",
                "collapsible": False,
                "items": [
                    {"title": "Unidades Escolares", "icon": "apartment", "link": reverse_lazy("admin:escola_unidadeescolar_changelist")},
                    {"title": "Convites",            "icon": "mail",      "link": reverse_lazy("admin:onboarding_conviteonboarding_changelist")},
                ],
            },
            {
                "title": "Equipe Escolar",
                "collapsible": False,
                "items": [
                    {"title": "Professores",   "icon": "school",  "link": reverse_lazy("admin:professor_perfilprofessor_changelist")},
                    {"title": "Colaboradores", "icon": "groups",  "link": reverse_lazy("admin:colaborador_perfilcolaborador_changelist")},
                    {"title": "Funções",       "icon": "badge",   "link": reverse_lazy("admin:colaborador_funcaoescolar_changelist")},
                ],
            },
            {
                "title": "Acadêmico",
                "collapsible": False,
                "items": [
                    {"title": "Anos Letivos",           "icon": "calendar_month",  "link": reverse_lazy("admin:ano_letivo_anoletivo_changelist")},
                    {"title": "Séries",                 "icon": "layers",          "link": reverse_lazy("admin:serie_serie_changelist")},
                    {"title": "Matérias",               "icon": "book_2",          "link": reverse_lazy("admin:materia_materia_changelist")},
                    {"title": "Alunos",                 "icon": "group",           "link": reverse_lazy("admin:aluno_aluno_changelist")},
                    {"title": "Matrículas",             "icon": "assignment",      "link": reverse_lazy("admin:aluno_matriculaturma_changelist")},
                    {"title": "Responsáveis",           "icon": "family_restroom", "link": reverse_lazy("admin:responsavel_perfilresponsavel_changelist")},
                    {"title": "Avaliações",             "icon": "quiz",            "link": reverse_lazy("admin:avaliacao_avaliacao_changelist")},
                    {"title": "Notas",                  "icon": "grade",           "link": reverse_lazy("admin:avaliacao_notaaluno_changelist")},
                    {"title": "Resultados Períodos",    "icon": "bar_chart",       "link": reverse_lazy("admin:boletim_resultadoperiodo_changelist")},
                    {"title": "Resultados Anuais",      "icon": "emoji_events",    "link": reverse_lazy("admin:boletim_resultadoanual_changelist")},
                    {"title": "Frequência (Registros)", "icon": "calendar_check",  "link": reverse_lazy("admin:frequencia_registrofrequencia_changelist")},
                    {"title": "Frequência (Presenças)", "icon": "how_to_reg",      "link": reverse_lazy("admin:frequencia_presencaaluno_changelist")},
                ],
            },
            {
                "title": "Financeiro",
                "collapsible": False,
                "items": [
                    {"title": "Planos",            "icon": "layers",       "link": reverse_lazy("admin:financeiro_planofinanceiro_changelist")},
                    {"title": "Cobranças",         "icon": "receipt_long", "link": reverse_lazy("admin:financeiro_cobrancaaluno_changelist")},
                    {"title": "Config. Financeira", "icon": "settings",    "link": reverse_lazy("admin:configuracao_configuracaofinanceira_changelist")},
                ],
            },
            {
                "title": "Monitoramento",
                "collapsible": False,
                "items": [
                    {"title": "Notificações", "icon": "notifications", "link": reverse_lazy("admin:notificacao_notificacao_changelist")},
                    {"title": "Auditoria",    "icon": "policy",        "link": reverse_lazy("admin:auditoria_logauditoria_changelist")},
                ],
            },
            {
                "title": "Autenticação",
                "collapsible": True,
                "items": [
                    {"title": "Grupos", "icon": "layers", "link": reverse_lazy("admin:auth_group_changelist")},
                ],
            },
        ],
    },
}
