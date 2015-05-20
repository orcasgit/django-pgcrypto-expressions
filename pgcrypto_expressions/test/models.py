from django.db import models

from pgcrypto_expressions.fields import ByteArrayField


class ByteArrayModel(models.Model):
    content = ByteArrayField(null=True)
