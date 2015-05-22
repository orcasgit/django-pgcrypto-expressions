from django.db import models

from pgcrypto_expressions import fields


class ByteArrayModel(models.Model):
    content = fields.ByteArrayField(null=True)


class EncryptedText(models.Model):
    value = fields.EncryptedTextField(default='hey', key='secret')


class RelatedText(models.Model):
    related = models.ForeignKey(EncryptedText)
    related_again = models.ForeignKey(EncryptedText, null=True)


class EncryptedInt(models.Model):
    value = fields.EncryptedIntegerField(null=True, key='secret')


class RelatedInt(models.Model):
    related = models.ForeignKey(EncryptedInt)
    related_again = models.ForeignKey(EncryptedInt, null=True)


class EncryptedDate(models.Model):
    value = fields.EncryptedDateField(key='secret')


class RelatedDate(models.Model):
    related = models.ForeignKey(EncryptedDate)
    related_again = models.ForeignKey(EncryptedDate, null=True)


class EncryptedUnique(models.Model):
    value = fields.EncryptedTextField(unique=True, key='secret')


class EncryptedIndex(models.Model):
    value = fields.EncryptedTextField(db_index=True, key='secret')
