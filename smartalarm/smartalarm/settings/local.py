from base import *

# Your Account Sid and Auth Token from twilio.com/user/account
TW_ACCOUNT_SID = "AC290ed2ca4fcedd8d4387b1193ff6e5e9"
TW_AUTH_TOKEN = "339e3728ab37609125aec0f0790f0370"

DEBUG = True

ALLOWED_HOSTS = ['localhost', '7a149f9a.ngrok.io', '10.1.5.59']

CORS_ORIGIN_WHITELIST = (
    'localhost:8001',
    'localhost:3000',
    'localhost',
    '7a149f9a.ngrok.io'
)

CORS_ALLOW_METHODS = (
    'GET',
    'POST',
)

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
