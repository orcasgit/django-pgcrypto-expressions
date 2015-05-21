from datetime import date, datetime

import pytest

from . import models, utils


class TestByteArrayField(object):
    def test_store_and_retrieve_bytearray(self, db):
        """Can store and retrieve data as bytearray."""
        data = bytearray([27, 23, 29, 33])
        models.ByteArrayModel.objects.create(content=data)
        found = models.ByteArrayModel.objects.get()

        assert found.content == data

    def test_store_null(self, db):
        """Conversion from db data doesn't choke on null/None."""
        models.ByteArrayModel.objects.create(content=None)
        found = models.ByteArrayModel.objects.get()

        assert found.content is None


RELATED = {
    models.EncryptedText: models.RelatedText,
    models.EncryptedInt: models.RelatedInt,
    models.EncryptedDate: models.RelatedDate,
}


@pytest.mark.parametrize(
    'model,vals',
    [
        (models.EncryptedText, ('foo', 'bar')),
        (models.EncryptedInt, (1, 2)),
        (models.EncryptedDate, (date(2015, 2, 5), date(2015, 2, 8))),
    ],
)
class TestEncryptedField(object):
    def test_insert(self, db, model, vals):
        """Data stored in DB is actually encrypted."""
        model.objects.create(value=vals[0])
        data = utils.decrypt_column_values(
            model, 'value', 'secret')

        coerce = {
            models.EncryptedText: lambda s: s,
            models.EncryptedInt: int,
            models.EncryptedDate: lambda s: datetime.strptime(s, '%Y-%m-%d').date()
        }[model]

        assert list(map(coerce, data)) == [vals[0]]

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

    def test_select_related(self, db, model, vals):
        """Can select related models with encrypted fields."""
        obj = model.objects.create(value=vals[0])
        related_model = RELATED[model]
        related_model.objects.create(related=obj)
        found = related_model.objects.select_related(
            'related'
        ).get()

        assert found.related.value == vals[0]

    def test_related_lookup(self, db, model, vals):
        """Can do joined lookups against encrypted fields."""
        obj = model.objects.create(value=vals[0])
        related_model = RELATED[model]
        related_model.objects.create(related=obj)
        found = related_model.objects.get(related__value=vals[0])

        assert found.related.value == vals[0]


class TestEncryptedTextField(object):
    def test_contains_lookup(self, db):
        """Can do __contains lookups against encrypted fields."""
        models.EncryptedText.objects.create(value='foobar')
        found = models.EncryptedText.objects.get(value__contains='oob')

        assert found.value == 'foobar'


class TestEncryptedIntegerField(object):
    def test_gt_lookup(self, db):
        """Can do __gt lookups against encrypted fields."""
        models.EncryptedInt.objects.create(value=4)
        found = models.EncryptedInt.objects.get(value__gt=3)

        assert found.value == 4

    def test_range_lookup(self, db):
        """Can do __range lookups against encrypted fields."""
        models.EncryptedInt.objects.create(value=4)
        found = models.EncryptedInt.objects.get(value__range=[3, 5])

        assert found.value == 4
