from django.db.backends.postgresql_psycopg2 import base
from pgcrypto_expressions.backends.mixin import DecryptedIndexMixin


class DatabaseWrapper(DecryptedIndexMixin, base.DatabaseWrapper):
    pass
