from django.db.models import TextField, Value as V

from pgcrypto_expressions import funcs
from .models import ByteArrayModel
from . import utils


class TestPgpSymEncrypt(object):
    def test_encrypt(self, db):
        ByteArrayModel.objects.create()
        ByteArrayModel.objects.update(
            content=funcs.PgpSymEncrypt(V('hello'), V('secret')))
        data = utils.decrypt_column_values(
            ByteArrayModel, 'content', 'secret')

        assert data == ["hello"]

    def test_decrypt(self, db):
        ByteArrayModel.objects.create()
        ByteArrayModel.objects.update(
            content=funcs.PgpSymEncrypt(V('hello'), V('secret')))
        found = ByteArrayModel.objects.annotate(
            decrypted=funcs.PgpSymDecrypt(
                'content', V('secret'), output_field=TextField())
        ).get()
        assert found.decrypted == "hello"
