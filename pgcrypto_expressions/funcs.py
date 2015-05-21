from django.db import models


class PgpSymEncrypt(models.Func):
    """The pgp_sym_encrypt function from pgcrypto.

    Takes two arguments: a text value to be encrypted, and the encryption
    key. Returns a bytea.

    """
    function = 'pgp_sym_encrypt'


class PgpSymDecrypt(models.Func):
    """The pgp_sym_decrypt function from pgcrypto.

    Takes two arguments: a bytea value to be decrypted, and the encryption
    key. Returns text.

    """
    function = 'pgp_sym_decrypt'
