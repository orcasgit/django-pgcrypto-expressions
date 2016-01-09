import platform

if platform.python_implementation() == 'PyPy':
    from psycopg2cffi import compat
    compat.register()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'djpgcetest',
        'TEST': {
            'NAME': 'djpgcetest',
        },
    },
    'secondary': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'djpgcetest_two',
        'TEST': {
            'NAME': 'djpgcetest_two',
        },
        'PGCRYPTO_KEY': 'secondary_key',
    },
}

INSTALLED_APPS = [
    'pgcrypto_expressions.test'
]

# Ensure that everything works even with a percent sign in the secret
SECRET_KEY = 'sec%ret'

SILENCED_SYSTEM_CHECKS = ['1_7.W001']
