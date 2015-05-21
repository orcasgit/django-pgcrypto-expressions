from .models import ByteArrayModel, EncryptedText
from . import utils


class TestByteArrayField(object):
    def test_store_and_retrieve_bytearray(self, db):
        """Can store and retrieve data as bytearray."""
        data = bytearray([27, 23, 29, 33])
        ByteArrayModel.objects.create(content=data)
        found = ByteArrayModel.objects.get()

        assert found.content == data

    def test_store_null(self, db):
        """Conversion from db data doesn't choke on null/None."""
        ByteArrayModel.objects.create(content=None)
        found = ByteArrayModel.objects.get()

        assert found.content is None


class TestEncryptedTextField(object):
    def test_insert(self, db):
        """Data stored in DB is actually encrypted."""
        EncryptedText.objects.create(text='foo')
        data = utils.decrypt_column_values(
            EncryptedText, 'text', 'secret')

        assert data == ['foo']

    def test_insert_and_select(self, db):
        """Data round-trips through insert and select."""
        EncryptedText.objects.create(text='foo')
        found = EncryptedText.objects.get()

        assert found.text == 'foo'

    def test_update_and_select(self, db):
        """Data round-trips through update and select."""
        EncryptedText.objects.create(text='foo')
        EncryptedText.objects.update(text='bar')
        found = EncryptedText.objects.get()

        assert found.text == 'bar'

    def test_lookup(self, db):
        """Can do exact lookups against encrypted field."""
        EncryptedText.objects.create(text='foo')
        found = EncryptedText.objects.get(text='foo')

        assert found.text == 'foo'
