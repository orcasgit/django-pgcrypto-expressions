from django.db import models

from pgcrypto_expressions import fields


class ByteArrayModel(models.Model):
    content = fields.ByteArrayField(null=True)


class EncryptedText(models.Model):
    text = fields.EncryptedField(models.TextField(), key='secret')
