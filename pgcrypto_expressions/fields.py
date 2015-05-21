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
    encrypt_sql_template = "pgp_sym_encrypt(%%s::text, '%(key)s')"
    decrypt_sql_template = "pgp_sym_decrypt(%%s, '%(key)s')::%(dbtype)s"

    """A field wrapper to encrypt any field type."""
    def __init__(self, wrapped_field, key, **kwargs):
        self.wrapped_field = wrapped_field
        self.wrapped_type = wrapped_field.db_type(connection)
        self.key = key
        self.encrypt_sql = self.encrypt_sql_template % {'key': key}
        self.decrypt_sql = self.decrypt_sql_template % {
            'key': key, 'dbtype': self.wrapped_type}
        super(EncryptedField, self).__init__(**kwargs)

    def db_type(self, connection):
        return 'bytea'

    def get_placeholder(self, value, compiler, connection):
        return self.encrypt_sql

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
