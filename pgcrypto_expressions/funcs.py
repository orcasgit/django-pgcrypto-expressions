from django.db import models


class PgpSymEncrypt(models.Func):
    function = 'pgp_sym_encrypt'


class PgpSymDecrypt(models.Func):
    function = 'pgp_sym_decrypt'
