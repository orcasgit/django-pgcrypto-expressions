from django.db import connection
from django.db.models import TextField, Value as V

from pgcrypto_expressions import funcs
from .models import ByteArrayModel


class TestPgpSymEncrypt(object):
    def test_encrypt(self, db):
        ByteArrayModel.objects.create()
        ByteArrayModel.objects.update(
            content=funcs.PgpSymEncrypt(V('hello'), V('secret')))
        with connection.cursor() as cur:
            cur.execute(
                "SELECT pgp_sym_decrypt(content, 'secret') "
                "FROM test_bytearraymodel"
            )
            data = cur.fetchone()[0]

        assert data == "hello"

    def test_decrypt(self, db):
        ByteArrayModel.objects.create()
        ByteArrayModel.objects.update(
            content=funcs.PgpSymEncrypt(V('hello'), V('secret')))
        found = ByteArrayModel.objects.annotate(
            decrypted=funcs.PgpSymDecrypt(
                'content', V('secret'), output_field=TextField())
        ).get()
        assert found.decrypted == "hello"
