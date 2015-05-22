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
    """A field wrapper to encrypt any field type.

    @@@ TODO:
    - handle aliased query (two joins to same table?)
    - handle any other field params passed to wrapped field?
    - handle field class-level flags (e.g. empty_strings_allowed)
    - handle custom implementations of various methods (get[_db]_prep*,
      to_python, from_db_value, formfield) on wrapped field
    - handle add-field migration
    - handle migration when secret changes (re-create indexes too)
    - make it easy to write a migration from a non-encrypted field to an
      encrypted field.
    - default secret key to a setting
    - docs (remember need for CREATE EXTENSION pgcrypto, custom backend)

    """
    encrypt_sql_template = "pgp_sym_encrypt(%%s::text, '%(key)s')"
    decrypt_sql_template = "pgp_sym_decrypt(%%s, '%(key)s')::%(dbtype)s"

    def __init__(self, wrapped_field, key):
        self.wrapped_field = wrapped_field
        # @@@ handle multi-db case, look for a PG connection
        self.wrapped_type = wrapped_field.db_type(connection)
        self.key = key
        self.encrypt_sql = self.encrypt_sql_template % {'key': key}
        self.decrypt_sql = self.decrypt_sql_template % {
            'key': key, 'dbtype': self.wrapped_type}
        super(EncryptedField, self).__init__()
        # We intentionally don't copy the db_index or unique properties of the
        # wrapped field, because indexes on the encrypted column are useless
        # (the custom backend creates indexes on the decrypt expression
        # instead, which are useful).
        self.verbose_name = self.wrapped_field.verbose_name
        self.name = self.wrapped_field.name
        self.null = self.wrapped_field.null
        self.default = self.wrapped_field.default

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

    def deconstruct(self):
        name, path, args, kwargs = super(EncryptedField, self).deconstruct()
        return name, path, [self.wrapped_field, self.key], {}


class DecryptedCol(Col):
    def __init__(self, alias, target, decrypt_sql, output_field=None):
        self.decrypt_sql = decrypt_sql
        super(DecryptedCol, self).__init__(alias, target, output_field)

    def as_sql(self, compiler, connection):
        sql, params = super(DecryptedCol, self).as_sql(compiler, connection)
        return self.decrypt_sql % sql, params
