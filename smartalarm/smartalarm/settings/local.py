from base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost']

CORS_ORIGIN_WHITELIST = (
    'localhost:8001',
    'localhost'
)

CORS_ALLOW_METHODS = (
    'GET',
)

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
