from datetime import date, datetime
from django.core.exceptions import ImproperlyConfigured

import pytest

from pgcrypto_expressions import fields
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


class TestEncryptedField(object):
    def test_name(self):
        f = fields.EncryptedTextField(name='field')

        assert f.name == 'field'

    def test_verbose_name(self):
        f = fields.EncryptedTextField("The Field")

        assert f.verbose_name == "The Field"

    def test_primary_key_not_allowed(self):
        with pytest.raises(ImproperlyConfigured):
            fields.EncryptedIntegerField(primary_key=True)

    def test_unique_not_allowed(self):
        with pytest.raises(ImproperlyConfigured):
            fields.EncryptedIntegerField(unique=True)

    def test_db_index_not_allowed(self):
        with pytest.raises(ImproperlyConfigured):
            fields.EncryptedIntegerField(db_index=True)

    def test_deconstruct(self):
        f = fields.EncryptedTextField()

        assert 'key' not in f.deconstruct()[3]

    def test_PGCRYPTO_KEY_setting(self, settings):
        settings.PGCRYPTO_KEY = 'other'
        f = fields.EncryptedTextField()

        assert f.key == 'other'


RELATED = {
    models.EncryptedText: models.RelatedText,
    models.EncryptedChar: models.RelatedChar,
    models.EncryptedEmail: models.RelatedEmail,
    models.EncryptedInt: models.RelatedInt,
    models.EncryptedDate: models.RelatedDate,
    models.EncryptedDateTime: models.RelatedDateTime,
}


@pytest.mark.parametrize(
    'model,vals',
    [
        (models.EncryptedText, ('foo', 'bar')),
        (models.EncryptedChar, ('one', 'two')),
        (models.EncryptedEmail, ('a@example.com', 'b@example.com')),
        (models.EncryptedInt, (1, 2)),
        (models.EncryptedDate, (date(2015, 2, 5), date(2015, 2, 8))),
        (
            models.EncryptedDateTime,
            (datetime(2015, 2, 5, 3), datetime(2015, 2, 8, 4))),
    ],
)
class TestEncryptedFieldQueries(object):
    def test_insert(self, db, model, vals):
        """Data stored in DB is actually encrypted."""
        field = model._meta.get_field('value')
        model.objects.create(value=vals[0])
        data = utils.decrypt_column_values(
            model, 'value', 'secret')

        assert list(map(field.to_python, data)) == [vals[0]]

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

    def test_double_select_related(self, db, model, vals):
        """Can select related the same model with an encrypted field twice."""
        obj = model.objects.create(value=vals[0])
        obj2 = model.objects.create(value=vals[1])
        related_model = RELATED[model]
        related_model.objects.create(related=obj, related_again=obj2)
        found = related_model.objects.select_related(
            'related', 'related_again',
        ).get()

        assert found.related.value == vals[0]
        assert found.related_again.value == vals[1]


class TestEncryptedTextField(object):
    def test_contains_lookup(self, db):
        """Can do __contains lookups against encrypted fields."""
        models.EncryptedText.objects.create(value='foobar')
        found = models.EncryptedText.objects.get(value__contains='oob')

        assert found.value == 'foobar'

    def test_default(self, db):
        """Field default values are respected."""
        models.EncryptedText.objects.create()
        found = models.EncryptedText.objects.get()

        assert found.value == 'hey'


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

    def test_nullable(self, db):
        """Encrypted field can be nullable."""
        models.EncryptedInt.objects.create(value=None)
        found = models.EncryptedInt.objects.get()

        assert found.value is None

    def test_ordering(self, db):
        """Can order by an encrypted field."""
        models.EncryptedInt.objects.create(value=5)
        models.EncryptedInt.objects.create(value=2)

        found = models.EncryptedInt.objects.order_by('value')

        assert [f.value for f in found] == [2, 5]
