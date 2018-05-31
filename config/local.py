from .settings import *  # NOQA

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pokeapi_co_db',
        'USER': 'root',
        'PASSWORD': 'pokeapi',
        'HOST': 'localhost',
        'PORT': '',
        'CONN_MAX_AGE': 30
    },
    # SQLite is not supported (doesn't have features required by cursor_pagination)
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

DEBUG = True
TASTYPIE_FULL_DEBUG = True

LOGGING = {
    'version': 1,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'config.middleware': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}

if DEBUG:
    # Log each db query to the console for debugging
    MIDDLEWARE_CLASSES = ('config.middleware.QueryDebugMiddleware',) + MIDDLEWARE_CLASSES

    # Log the number of queries and the total run time to the console
    MIDDLEWARE_CLASSES = ('config.middleware.QueryCountDebugMiddleware',) + MIDDLEWARE_CLASSES
