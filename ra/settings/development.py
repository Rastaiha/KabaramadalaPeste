from ra.settings.base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*z!3aidedw32xh&1ew(^&5dgd17(ynnmk=s*mo=v2l_(4t_ff('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
