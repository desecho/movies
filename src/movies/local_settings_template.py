DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "movies",
        "USER": "root",
        "PASSWORD": "password",
        "HOST": "127.0.0.1",
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    }
}
SECRET_KEY = "key"
PROJECT_DOMAIN = "localhost"
RAVEN_DSN = ""
GOOGLE_ANALYTICS_ID = "id"
ADMIN_EMAIL = ""

DEBUG = True
INTERNAL_IPS = []

IS_VK_DEV = False
HOST_MOVIES_TEST = ""

SOCIAL_AUTH_VK_APP_KEY = ""
SOCIAL_AUTH_VK_APP_SECRET = ""

SOCIAL_AUTH_VK_OAUTH2_KEY = ""
SOCIAL_AUTH_VK_OAUTH2_SECRET = ""

SOCIAL_AUTH_FACEBOOK_KEY = ""
SOCIAL_AUTH_FACEBOOK_SECRET = ""

TMDB_KEY = ""
OMDB_KEY = ""

EMAIL_USE_SSL = True
EMAIL_HOST = ""
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_PORT = ""
