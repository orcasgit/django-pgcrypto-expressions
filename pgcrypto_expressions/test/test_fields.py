import pytest

from .models import ByteArrayModel, EncryptedText, EncryptedInt
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


@pytest.mark.parametrize(
    'model,vals',
    [
        (EncryptedText, ('foo', 'bar')),
        (EncryptedInt, (1, 2)),
    ],
)
class TestEncryptedField(object):
    def test_insert(self, db, model, vals):
        """Data stored in DB is actually encrypted."""
        model.objects.create(value=vals[0])
        data = utils.decrypt_column_values(
            model, 'value', 'secret')

        assert list(map(type(vals[0]), data)) == [vals[0]]

    def test_insert_and_select(self, db, model, vals):
        """Data round-trips through insert and select."""
        model.objects.create(value=vals[0])
        found = model.objects.get()

        assert found.value == vals[0]

    def test_update_and_select(self, db, model, vals):
        """Data round-trips through update and select."""
        model.objects.create(value=vals[0])
        model.objects.update(value=vals[1])
        found = model.objects.get()

        assert found.value == vals[1]

    def test_exact_lookup(self, db, model, vals):
        """Can do exact lookups against encrypted fields."""
        model.objects.create(value=vals[0])
        found = model.objects.get(value=vals[0])

        assert found.value == vals[0]

    def test_in_lookup(self, db, model, vals):
        """Can do __in lookups against encrypted fields."""
        model.objects.create(value=vals[0])
        found = model.objects.get(value__in=vals)

        assert found.value == vals[0]


class TestEncryptedTextField(object):
    def test_contains_lookup(self, db):
        """Can do __contains lookups against encrypted fields."""
        EncryptedText.objects.create(value='foobar')
        found = EncryptedText.objects.get(value__contains='oob')

        assert found.value == 'foobar'


class TestEncryptedIntegerField(object):
    def test_gt_lookup(self, db):
        """Can do __gt lookups against encrypted fields."""
        EncryptedInt.objects.create(value=4)
        found = EncryptedInt.objects.get(value__gt=3)

        assert found.value == 4

    def test_range_lookup(self, db):
        """Can do __range lookups against encrypted fields."""
        EncryptedInt.objects.create(value=4)
        found = EncryptedInt.objects.get(value__range=[3, 5])

        assert found.value == 4
