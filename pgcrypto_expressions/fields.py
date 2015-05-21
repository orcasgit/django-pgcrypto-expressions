from django.db import models


class ByteArrayField(models.Field):
    """A simple field type for the Postgres bytea type.

    Represents values as bytearray instances in Python.

    Mostly exists to facilitate testing of the Funcs in this package, but you
    can certainly use it if you need it.

    """
    def db_type(self, connection):
        return 'bytea'

    def from_db_value(self, value, expression, connection, context):
        if value is not None:
            return bytearray(value)
