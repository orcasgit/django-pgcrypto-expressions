from .models import ByteArrayModel


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
