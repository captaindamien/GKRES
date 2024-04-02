from .base import *
import environ

env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['gkres.ru']
CSRF_TRUSTED_ORIGINS = ['https://gkres.ru']

try:
    from .local import *
except ImportError:
    pass
