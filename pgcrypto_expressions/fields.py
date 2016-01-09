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
    encrypt_sql_template = "pgp_sym_encrypt(%s::text, '{key}')"
    decrypt_sql_template = "pgp_sym_decrypt({sql}, '{key}')::{dbtype}"

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

    def db_type(self, connection):
        return 'bytea'

    def _get_encryption_key(self, connection):
        if 'PGCRYPTO_KEY' in connection.settings_dict:
            key = connection.settings_dict['PGCRYPTO_KEY']
        else:
            key = getattr(settings, 'PGCRYPTO_KEY', settings.SECRET_KEY)
        # Escape any percent symbols in the key, to avoid them being
        # interpreted as extra substitution placeholders later on.
        key = key.replace('%', '%%')
        return key

    def get_placeholder(self, value, compiler, connection):
        key = self._get_encryption_key(connection)
        return self.encrypt_sql_template.format(key=key)

    def get_col(self, alias, output_field=None):
        if output_field is None:
            output_field = self
        if alias != self.model._meta.db_table or output_field != self:
            return DecryptedCol(alias, self, self.decrypt_sql_template,
                                output_field)
        else:
            return self.cached_col

    @cached_property
    def cached_col(self):
        return DecryptedCol(
            self.model._meta.db_table,
            self,
            self.decrypt_sql_template,
        )


class DecryptedCol(Col):
    def __init__(self, alias, target, decrypt_sql_template, output_field=None):
        self.decrypt_sql_template = decrypt_sql_template
        self.target = target
        super(DecryptedCol, self).__init__(alias, target, output_field)

    def as_sql(self, compiler, connection):
        key = self.target._get_encryption_key(connection)
        decrypt_sql = self.decrypt_sql_template.format(
            key=key,
            dbtype=self.target.base_db_type,
            sql='{sql}'
        )
        sql, params = super(DecryptedCol, self).as_sql(compiler, connection)
        return decrypt_sql.format(sql=sql), params


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
