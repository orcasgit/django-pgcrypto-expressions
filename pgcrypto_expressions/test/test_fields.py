from .models import ByteArrayModel, EncryptedText
from . import utils


class TestByteArrayField(object):
    def test_store_and_retrieve_bytearray(self, db):
        data = bytearray([27, 23, 29, 33])
        ByteArrayModel.objects.create(content=data)
        found = ByteArrayModel.objects.get()

        assert found.content == data

    def test_store_null(self, db):
        ByteArrayModel.objects.create(content=None)
        found = ByteArrayModel.objects.get()

        assert found.content is None


class TestEncryptedTextField(object):
    def test_create(self, db):
        EncryptedText.objects.create(text='foo')
        data = utils.decrypt_column_values(
            EncryptedText, 'text', 'secret')

        assert data == ['foo']

    def test_create_and_query(self, db):
        EncryptedText.objects.create(text='foo')
        found = EncryptedText.objects.get()

        assert found.text == 'foo'
