from django.db import models

from pgcrypto_expressions import fields


class ByteArrayModel(models.Model):
    content = fields.ByteArrayField(null=True)


class EncryptedText(models.Model):
    value = fields.EncryptedField(
        models.TextField(default='hey'), key='secret')


class RelatedText(models.Model):
    related = models.ForeignKey(EncryptedText)


class EncryptedInt(models.Model):
    value = fields.EncryptedField(models.IntegerField(null=True), key='secret')


class RelatedInt(models.Model):
    related = models.ForeignKey(EncryptedInt)


class EncryptedDate(models.Model):
    value = fields.EncryptedField(models.DateField(), key='secret')


class RelatedDate(models.Model):
    related = models.ForeignKey(EncryptedDate)


class EncryptedUnique(models.Model):
    value = fields.EncryptedField(
        models.TextField(unique=True), key='secret')


class EncryptedIndex(models.Model):
    value = fields.EncryptedField(
        models.TextField(db_index=True), key='secret')
