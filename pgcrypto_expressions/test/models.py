from django.db import models

from pgcrypto_expressions import fields


class ByteArrayModel(models.Model):
    content = fields.ByteArrayField(null=True)


class EncryptedText(models.Model):
    value = fields.EncryptedField(models.TextField(), key='secret')


class EncryptedInt(models.Model):
    value = fields.EncryptedField(models.IntegerField(), key='secret')


class EncryptedDate(models.Model):
    value = fields.EncryptedField(models.DateField(), key='secret')
