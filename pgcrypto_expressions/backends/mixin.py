from django.db.backends.postgresql_psycopg2 import base

from ..fields import EncryptedFieldMixin


class DatabaseSchemaEditor(base.DatabaseSchemaEditor):
    # We can't use self.sql_create_unique, because that adds a unique
    # constraint rather than a unique index, and PostgreSQL doesn't allow
    # unique constraints on expressions. Unique indexes on expressions are
    # allowed and have the same effect as a constraint.
    sql_create_unique_index = (
        base.DatabaseSchemaEditor.sql_create_index.replace(
            'CREATE INDEX', 'CREATE UNIQUE INDEX')
    )

    def _model_indexes_sql(self, model):
        """
        Return all index SQL statements (field indexes, index_together) for the
        specified model, as a list.
        """
        output = super(DatabaseSchemaEditor, self)._model_indexes_sql(model)
        for field in model._meta.fields:
            if isinstance(field, EncryptedFieldMixin):
                output.extend(self._encrypted_field_indexes_sql(model, field))
        return output

    def _encrypted_field_indexes_sql(self, model, field):
        output = []
        table = model._meta.db_table
        decrypt = '(%s)' % (field.decrypt_sql % field.column)
        create = False
        unique = False
        if field.unique:
            create = unique = True
        elif field.db_index:
            create = True
        if create:
            suffix = '_decrypt_uniq' if unique else '_decrypt'
            template = (
                self.sql_create_unique_index
                if unique
                else self.sql_create_index
            )
            sql = template % {
                'table': table,
                'name': self._create_index_name(model, [field.column], suffix),
                'columns': decrypt,
                'extra': '',
            }
            output.append(sql)
        return output


class DecryptedIndexMixin(object):
    SchemaEditorClass = DatabaseSchemaEditor
