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


class EncryptedFieldMixin(models.Field):
    """A field mixin to encrypt any field type.

    @@@ TODO:
    - handle add-field migration
    - handle migration when secret changes (re-create indexes too)
    - make it easy to write a migration from a non-encrypted field to an
      encrypted field.
    - default secret key to a setting
    - docs (remember need for CREATE EXTENSION pgcrypto, custom backend)

    """
    encrypt_sql_template = "pgp_sym_encrypt(%%s::text, '%(key)s')"
    decrypt_sql_template = "pgp_sym_decrypt(%%s, '%(key)s')::%(dbtype)s"

    def __init__(self, *args, **kwargs):
        if kwargs.get('primary_key'):
            raise ImproperlyConfigured(
                "EncryptedFieldMixin does not support primary key fields."
            )
        self.key = kwargs.pop('key')
        super(EncryptedFieldMixin, self).__init__(*args, **kwargs)
        # @@@ handle multi-db case, look for a PG connection
        self.base_db_type = super(
            EncryptedFieldMixin, self
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

    def deconstruct(self):
        name, path, args, kwargs = super(
            EncryptedFieldMixin, self
        ).deconstruct()
        kwargs['key'] = self.key
        return name, path, args, kwargs


class DecryptedCol(Col):
    def __init__(self, alias, target, decrypt_sql, output_field=None):
        self.decrypt_sql = decrypt_sql
        super(DecryptedCol, self).__init__(alias, target, output_field)

    def as_sql(self, compiler, connection):
        sql, params = super(DecryptedCol, self).as_sql(compiler, connection)
        return self.decrypt_sql % sql, params


class EncryptedTextField(EncryptedFieldMixin, models.TextField):
    pass


class EncryptedIntegerField(EncryptedFieldMixin, models.IntegerField):
    pass


class EncryptedDateField(EncryptedFieldMixin, models.DateField):
    pass
