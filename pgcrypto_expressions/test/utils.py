from django.db import connection


def decrypt_column_values(model, field_name, secret):
    """Return decrypted column values as list, direct from db."""
    with connection.cursor() as cur:
        cur.execute(
            "SELECT pgp_sym_decrypt(%(field_name)s, '%(secret)s') "
            "FROM %(table_name)s" % {
                'field_name': field_name,
                'secret': secret,
                'table_name': model._meta.db_table
            }
        )
        return [row[0] for row in cur.fetchall()]
