from django.db.backends.postgresql_psycopg2 import base

from ..fields import EncryptedField


class DatabaseSchemaEditor(base.DatabaseSchemaEditor):
    def _model_indexes_sql(self, model):
        """
        Return all index SQL statements (field indexes, index_together) for the
        specified model, as a list.
        """
        output = super(DatabaseSchemaEditor, self)._model_indexes_sql(model)
        for field in model._meta.fields:
            if isinstance(field, EncryptedField):
                output.extend(self._encrypted_field_indexes_sql(model, field))
        return output

    def _encrypted_field_indexes_sql(self, model, field):
        output = []
        table = model._meta.db_table
        column = '(%s)' % (field.decrypt_sql % field.column)
        if field.wrapped_field.unique:
            # We can't use self.sql_create_unique, because that adds a unique
            # constraint rather than a unique index, and PostgreSQL doesn't
            # allow unique constraints on expressions, whereas unique indexes
            # on expressions are allowed and have the same effect.
            sql = self.sql_create_index % {
                'table': table,
                'name': self._create_index_name(
                    model, [field.column], '_decrypt_uniq'),
                'columns': column,
                'extra': '',
            }
            output.append(sql.replace('CREATE INDEX', 'CREATE UNIQUE INDEX'))
        return output


class DecryptedIndexMixin(object):
    SchemaEditorClass = DatabaseSchemaEditor
