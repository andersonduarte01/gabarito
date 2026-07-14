from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
from django.conf.global_settings import STATIC_ROOT, MEDIA_URL, AUTH_USER_MODEL, LOGIN_REDIRECT_URL, LOGIN_URL

BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure--piij5(*ab&p8#vua9g4()hm7k2=*r)xw&_lycn42eodwoo2#9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.core.middleware.TenantMiddleware',
    # 'hijack.middleware.HijackUserMiddleware',
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


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'system',
#         'USER': 'root',
#         'PASSWORD': 'sosa1808',
#         'HOST': 'localhost',
#         'PORT': '3306',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True

DATE_INPUT_FORMATS = ['%d/%m/%Y']

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
CKEDITOR_UPLOAD_PATH = "media/Noticias"
# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'core.Usuario'

LOGIN_URL           = '/accounts/login/'
LOGIN_REDIRECT_URL  = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

#CKEDITOR
CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono',
        # 'skin': 'office2013',
        'toolbar_Basic': [
            ['Source', '-', 'Bold', 'Italic']
        ],
        'toolbar_YourCustomToolbarConfig': [
            {'name': 'document', 'items': ['Source', '-', 'Save', 'NewPage', 'Preview', 'Print', '-', 'Templates']},
            {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
            {'name': 'editing', 'items': ['Find', 'Replace', '-', 'SelectAll']},
            {'name': 'forms',
             'items': ['Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton',
                       'HiddenField']},
            '/',
            {'name': 'basicstyles',
             'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl',
                       'Language']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert',
             'items': ['Image', 'Flash', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak', 'Iframe']},
            '/',
            {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'tools', 'items': ['Maximize', 'ShowBlocks']},
            {'name': 'about', 'items': ['About']},
            '/',  # put this to force next toolbar on new line
            {'name': 'yourcustomtools', 'items': [
                # put the name of your editor.ui.addButton here
                'Preview',
                'Maximize',

            ]},
        ],
        'toolbar': 'YourCustomToolbarConfig',  # put selected toolbar config here
        # 'toolbarGroups': [{ 'name': 'document', 'groups': [ 'mode', 'document', 'doctools' ] }],
        # 'height': 291,
        # 'width': '100%',
        # 'filebrowserWindowHeight': 725,
        # 'filebrowserWindowWidth': 940,
        # 'toolbarCanCollapse': True,
        # 'mathJaxLib': '//cdn.mathjax.org/mathjax/2.2-latest/MathJax.js?config=TeX-AMS_HTML',
        'tabSpaces': 4,
        'extraPlugins': ','.join([
            'uploadimage', # the upload image feature
            # your extra plugins here
            'div',
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            # 'devtools',
            'widget',
            'lineutils',
            'clipboard',
            'dialog',
            'dialogui',
            'elementspath'
        ]),
    }
}


# RESET DE SENHA
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = str(BASE_DIR.joinpath('sent_emails'))

from datetime import timedelta
from django.urls import reverse_lazy

# ---------------------------------------------------------------------------
# Django Unfold — Admin Theme
# ---------------------------------------------------------------------------

UNFOLD = {
    "SITE_TITLE":  "EduCare Admin",
    "SITE_HEADER": "EduCare",
    "SITE_URL":    "/",
    "SITE_SYMBOL": "school",
    "SHOW_HISTORY":      True,
    "SHOW_VIEW_ON_SITE": True,

    # Bootstrap 5 blue (#0d6efd = rgb 13 110 253) como cor primária
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
                    {
                        "title": "Planos",
                        "icon":  "deployed_code",
                        "link":  reverse_lazy("admin:planos_plano_changelist"),
                    },
                    {
                        "title": "Assinaturas",
                        "icon":  "task_alt",
                        "link":  reverse_lazy("admin:planos_assinaturaescola_changelist"),
                    },
                    {
                        "title": "Módulos",
                        "icon":  "extension",
                        "link":  reverse_lazy("admin:planos_modulo_changelist"),
                    },
                ],
            },
            {
                "title": "Controle de Acesso",
                "collapsible": False,
                "items": [
                    {
                        "title": "Usuários",
                        "icon":  "group",
                        "link":  reverse_lazy("admin:core_usuario_changelist"),
                    },
                    {
                        "title": "Vínculos",
                        "icon":  "swap_horiz",
                        "link":  reverse_lazy("admin:core_vinculoescola_changelist"),
                    },
                    {
                        "title": "Papéis",
                        "icon":  "verified_user",
                        "link":  reverse_lazy("admin:core_papelvinculo_changelist"),
                    },
                ],
            },
            {
                "title": "Escolas",
                "collapsible": False,
                "items": [
                    {
                        "title": "Unidades Escolares",
                        "icon":  "apartment",
                        "link":  reverse_lazy("admin:escola_unidadeescolar_changelist"),
                    },
                    {
                        "title": "Convites",
                        "icon":  "mail",
                        "link":  reverse_lazy("admin:onboarding_conviteonboarding_changelist"),
                    },
                ],
            },
            {
                "title": "Equipe Escolar",
                "collapsible": False,
                "items": [
                    {
                        "title": "Professores",
                        "icon":  "school",
                        "link":  reverse_lazy("admin:professor_perfilprofessor_changelist"),
                    },
                    {
                        "title": "Colaboradores",
                        "icon":  "groups",
                        "link":  reverse_lazy("admin:colaborador_perfilcolaborador_changelist"),
                    },
                    {
                        "title": "Funções",
                        "icon":  "badge",
                        "link":  reverse_lazy("admin:colaborador_funcaoescolar_changelist"),
                    },
                ],
            },
            {
                "title": "Acadêmico",
                "collapsible": False,
                "items": [
                    {
                        "title": "Anos Letivos",
                        "icon":  "calendar_month",
                        "link":  reverse_lazy("admin:ano_letivo_anoletivo_changelist"),
                    },
                    {
                        "title": "Séries",
                        "icon":  "layers",
                        "link":  reverse_lazy("admin:serie_serie_changelist"),
                    },
                    {
                        "title": "Matérias",
                        "icon":  "book_2",
                        "link":  reverse_lazy("admin:materia_materia_changelist"),
                    },
                    {
                        "title": "Alunos",
                        "icon":  "group",
                        "link":  reverse_lazy("admin:aluno_aluno_changelist"),
                    },
                    {
                        "title": "Matrículas",
                        "icon":  "assignment",
                        "link":  reverse_lazy("admin:aluno_matriculaturma_changelist"),
                    },
                    {
                        "title": "Responsáveis",
                        "icon":  "family_restroom",
                        "link":  reverse_lazy("admin:responsavel_perfilresponsavel_changelist"),
                    },
                    {
                        "title": "Avaliações",
                        "icon":  "quiz",
                        "link":  reverse_lazy("admin:avaliacao_avaliacao_changelist"),
                    },
                    {
                        "title": "Notas",
                        "icon":  "grade",
                        "link":  reverse_lazy("admin:avaliacao_notaaluno_changelist"),
                    },
                    {
                        "title": "Resultados Períodos",
                        "icon":  "bar_chart",
                        "link":  reverse_lazy("admin:boletim_resultadoperiodo_changelist"),
                    },
                    {
                        "title": "Resultados Anuais",
                        "icon":  "emoji_events",
                        "link":  reverse_lazy("admin:boletim_resultadoanual_changelist"),
                    },
                    {
                        "title": "Frequência (Registros)",
                        "icon":  "calendar_check",
                        "link":  reverse_lazy("admin:frequencia_registrofrequencia_changelist"),
                    },
                    {
                        "title": "Frequência (Presenças)",
                        "icon":  "how_to_reg",
                        "link":  reverse_lazy("admin:frequencia_presencaaluno_changelist"),
                    },
                ],
            },
            {
                "title": "Financeiro",
                "collapsible": False,
                "items": [
                    {
                        "title": "Planos",
                        "icon":  "layers",
                        "link":  reverse_lazy("admin:financeiro_planofinanceiro_changelist"),
                    },
                    {
                        "title": "Cobranças",
                        "icon":  "receipt_long",
                        "link":  reverse_lazy("admin:financeiro_cobrancaaluno_changelist"),
                    },
                    {
                        "title": "Config. Financeira",
                        "icon":  "settings",
                        "link":  reverse_lazy("admin:configuracao_configuracaofinanceira_changelist"),
                    },
                ],
            },
            {
                "title": "Monitoramento",
                "collapsible": False,
                "items": [
                    {
                        "title": "Notificações",
                        "icon":  "notifications",
                        "link":  reverse_lazy("admin:notificacao_notificacao_changelist"),
                    },
                    {
                        "title": "Auditoria",
                        "icon":  "policy",
                        "link":  reverse_lazy("admin:auditoria_logauditoria_changelist"),
                    },
                ],
            },
            {
                "title": "Autenticação",
                "collapsible": True,
                "items": [
                    {
                        "title": "Grupos",
                        "icon":  "layers",
                        "link":  reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
        ],
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=3650),  # 10 anos, por exemplo
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
TAILWIND_APP_NAME = 'theme'
if os.name == 'nt':
    NPM_BIN_PATH = r"C:\Program Files\nodejs\npm.cmd"