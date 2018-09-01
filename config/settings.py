# Production settings
from unipath import Path
import os

PROJECT_ROOT = Path(__file__).ancestor(2)

DEBUG = False

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Paul Hallett', 'paulandrewhallett@gmail.com'),
)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MANAGERS = ADMINS

BASE_URL = 'http://pokeapi.co'

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['.pokeapi.co', 'localhost']

TIME_ZONE = 'Europe/London'

LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Explicitly define test runner to avoid warning messages on test execution
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

MEDIA_ROOT = PROJECT_ROOT.child('media')

MEDIA_URL = '/media/'

STATIC_ROOT = PROJECT_ROOT.child('assets')

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
    # '/pokemon/assets/',
    # 'pokemon_v2/assets/',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SECRET_KEY = '4nksdock439320df*(^x2_scm-o$*py3e@-awu-n^hipkm%2l$sw$&2l#'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

# TEMPLATE_DIRS = (
#     PROJECT_ROOT.child('templates'),
# )
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [PROJECT_ROOT.child('templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # 'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                # 'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pokeapi_co_db',
        'USER': 'root',
        'PASSWORD': 'pokeapi',
        'HOST': 'localhost',
        'PORT': '',
        'CONN_MAX_AGE': 30
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'ubx+22!jbo(^x2_scm-o$*py3e@-awu-n^hipkm%2l$sw$&2l#')

CUSTOM_APPS = (
    'tastypie',
    'pokemon',
    'pokemon_v2',
    'pokemon_graphql',
    'hits',
    'alerts',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.humanize',
    'corsheaders',
    'rest_framework',
    'markdown_deux',
    'cachalot',
    'graphene_django',
    'webpack_loader',
    'menuware',
) + CUSTOM_APPS


API_LIMIT_PER_PAGE = 1

TASTYPIE_DEFAULT_FORMATS = ['json']

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_METHODS = (
    'GET', 'POST'
)

CORS_URLS_REGEX = r'^(/api/|/graphql/|/graphql).*$'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'drf_ujson.renderers.UJSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'drf_ujson.renderers.UJSONRenderer',
    ),

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',

    'PAGE_SIZE': 20,

    'PAGINATE_BY': 20,
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/hour'
    }
}

MARKDOWN_DEUX_STYLES = {
    "default": {
        "extras": {
            "code-friendly": None,
            "tables": None,
            "fenced-code-blocks": None,
            "header-ids": None
        },
        "safe_mode": False,
    },
}

# Stripe

STRIPE_TEST_SECRET_KEY = os.environ.get('STRIPE_TEST_SECRET_KEY', '')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
STRIPE_TEST_PUBLISHABLE_KEY = os.environ.get('STRIPE_TEST_PUBLISHABLE_KEY', '')

if DEBUG:
    STRIPE_KEYS = {
        "secret": STRIPE_TEST_SECRET_KEY,
        "publishable": STRIPE_TEST_PUBLISHABLE_KEY
    }
else:
    STRIPE_KEYS = {
        "secret": STRIPE_SECRET_KEY,
        "publishable": STRIPE_PUBLISHABLE_KEY
    }

GRAPHENE = {
    'MIDDLEWARE': [
        'pokemon_graphql.middleware.LoaderMiddleware'
    ],
}

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'bundles/',
        'STATS_FILE': os.path.join(PROJECT_ROOT, 'webpack-stats.json'),
    }
}


MAIN_MENU = [
    {
        "name": "Home",
        "url": "config.views.home",  # reversible
    },
    {
        "name": "About",
        "url": "config.views.about",  # reversible
    },
    {
        "name": "Explore",
        "url": "#",
        "submenu": [
            {
                "name": "GraphQL",
                "url": "/explore/graphql/",
            },
            {
                "name": "RESTful V2",
                "url": "/explore/v2/",
            },
        ],
    },
    {
        "name": "Documentation",
        "url": "#",
        "submenu": [
            {
                "name": "GraphQL",
                "url": "/docs/graphql/",
            },
            {
                "name": "RESTful V2",
                "url": "/docs/v2/",
            },
            {
                "name": "RESTful V1 (deprecated)",
                "url": "/docs/v1/",
            },
        ],
    },
]

# DOCS_VERSION_SELECT_MENU = [
#     {
#         "name": "GraphQL",
#         "url": "/docs/graphql/",
#     },
#     {
#         "name": "REST (V2)",
#         "url": "/docs/v2/",
#     },
#     {
#         "name": "REST (V1) -. deprecated",
#         "url": "/docs/v1/",
#     },
# ]
