from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import connection, models
from django.db.models.expressions import Col
from django.utils.functional import cached_property


class ByteArrayField(models.Field):
    """A simple field type for the Postgres bytea type.

    Represents values as bytearray instances in Python.

    """
    def db_type(self, connection):
        return 'bytea'

    def from_db_value(self, value, expression, connection, context):
        if value is not None:
            return bytearray(value)


class EncryptedField(models.Field):
    """A field mixin to encrypt any field type using pgcrypto.

    """
    encrypt_sql_template = "pgp_sym_encrypt(%%s::text, '%(key)s')"
    decrypt_sql_template = "pgp_sym_decrypt(%%s, '%(key)s')::%(dbtype)s"

    def __init__(self, *args, **kwargs):
        if kwargs.get('primary_key'):
            raise ImproperlyConfigured(
                "EncryptedField does not support primary key fields."
            )
        if kwargs.get('unique'):
            raise ImproperlyConfigured(
                "EncryptedField does not support unique fields."
            )
        if kwargs.get('db_index'):
            raise ImproperlyConfigured(
                "EncryptedField does not support indexing fields."
            )
        self.key = getattr(settings, 'PGCRYPTO_KEY', settings.SECRET_KEY)
        super(EncryptedField, self).__init__(*args, **kwargs)
        # @@@ handle multi-db case, look for a PG connection
        self.base_db_type = super(
            EncryptedField, self
        ).db_type(connection)
        self.encrypt_sql = self.encrypt_sql_template % {'key': self.key}
        self.decrypt_sql = self.decrypt_sql_template % {
            'key': self.key, 'dbtype': self.base_db_type}

    def db_type(self, connection):
        return 'bytea'

    def get_placeholder(self, value, compiler, connection):
        return self.encrypt_sql

    def get_col(self, alias, output_field=None):
        if output_field is None:
            output_field = self
        if alias != self.model._meta.db_table or output_field != self:
            return DecryptedCol(alias, self, self.decrypt_sql, output_field)
        else:
            return self.cached_col

    @cached_property
    def cached_col(self):
        return DecryptedCol(
            self.model._meta.db_table,
            self,
            self.decrypt_sql,
        )


class DecryptedCol(Col):
    def __init__(self, alias, target, decrypt_sql, output_field=None):
        self.decrypt_sql = decrypt_sql
        super(DecryptedCol, self).__init__(alias, target, output_field)

    def as_sql(self, compiler, connection):
        sql, params = super(DecryptedCol, self).as_sql(compiler, connection)
        return self.decrypt_sql % sql, params


class EncryptedTextField(EncryptedField, models.TextField):
    pass


class EncryptedCharField(EncryptedField, models.CharField):
    pass


class EncryptedEmailField(EncryptedField, models.EmailField):
    pass


class EncryptedIntegerField(EncryptedField, models.IntegerField):
    pass


class EncryptedDateField(EncryptedField, models.DateField):
    pass


class EncryptedDateTimeField(EncryptedField, models.DateTimeField):
    pass
