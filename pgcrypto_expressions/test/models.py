from django.db import models

from pgcrypto_expressions import fields


class ByteArrayModel(models.Model):
    content = fields.ByteArrayField(null=True)


class EncryptedText(models.Model):
    value = fields.EncryptedTextField(default='hey')


class RelatedText(models.Model):
    related = models.ForeignKey(EncryptedText)
    related_again = models.ForeignKey(EncryptedText, null=True)


class EncryptedChar(models.Model):
    value = fields.EncryptedCharField(max_length=25)


class RelatedChar(models.Model):
    related = models.ForeignKey(EncryptedChar)
    related_again = models.ForeignKey(EncryptedChar, null=True)


class EncryptedEmail(models.Model):
    value = fields.EncryptedEmailField(default='hey')


class RelatedEmail(models.Model):
    related = models.ForeignKey(EncryptedEmail)
    related_again = models.ForeignKey(EncryptedEmail, null=True)


class EncryptedInt(models.Model):
    value = fields.EncryptedIntegerField(null=True)


class RelatedInt(models.Model):
    related = models.ForeignKey(EncryptedInt)
    related_again = models.ForeignKey(EncryptedInt, null=True)


class EncryptedDate(models.Model):
    value = fields.EncryptedDateField()


class RelatedDate(models.Model):
    related = models.ForeignKey(EncryptedDate)
    related_again = models.ForeignKey(EncryptedDate, null=True)


class EncryptedDateTime(models.Model):
    value = fields.EncryptedDateTimeField()


class RelatedDateTime(models.Model):
    related = models.ForeignKey(EncryptedDateTime)
    related_again = models.ForeignKey(EncryptedDateTime, null=True)
