Google Sheet Keyring backend
============================

|PyPI version| |Doc Status| |License| |Supported Python|

This package provides a Keyring_ backend that stores passwords in a Google
Sheet.

Motivation
----------

This package allows ipython-secrets_ to be used on Google Colaboratory, and on
other hosted services that don’t support the standard Keyring backends.

The **ipython-secrets** package uses Keyring to store secrets for use in a Jupyter
notebook. However, none of the standard Keyring backends works in `Google
Colaboratory`_, since that service provides neither durable file storage, nor
the native operating system services that the standard keyring backends require.

Usage
-----

To use this package, install it via ``pip3 install gsheet-keyring``, and use the
`Keyring API`_ as normal. If one of the built-in Keyring backends is available,
Keyring will use that backend in preference to this one (as it should). However,
if a platform-specific backend is not available, Keyring will automatically
detect and use this package instead.

Use ``keyring.set_keyring`` to force Keyring to use this package even, if other
backends are available:

.. code:: python

   import keyring
   from gsheet_keyring import GoogleSheetKeyring
   keyring.set_keyring(GoogleSheetKeyring())

By default, this backend searches for a Google Sheet named “keyring”. If there’s
no sheet with this name, one is created.

You can override this default by specifying a Google Sheet name, a Google Sheet
key, or a ``Worksheet`` from the `gspread`_ package.

Alternatives
------------

If you're running in an environment where any other Keyring backend is
available, use that instead. (This should happen automatically.)

If you require either greater performance or security than this package provides
(see the notes in the API documentation), you probably want to instead create or
use a backend that uses a secret management service such `AWS Secrets Manager
<https://aws.amazon.com/secrets-manager/>`_, `Google Cloud AMS
<https://cloud.google.com/kms/docs/secret-management>`_, or or `Hashicorp Vault
<https://www.vaultproject.io/>`_.

The `keyring-vault-backend package
<https://github.com/pschmitt/keyring-vault-backend>`_ is a Keyring backend
interface to Hashicorp Vault. I haven't used it.

License
-------

MIT

.. |PyPI version| image:: https://img.shields.io/pypi/v/gsheet-keyring.svg
    :target: https://pypi.python.org/pypi/gsheet-keyring
    :alt: Latest PyPI Version
.. |Doc Status| image:: https://readthedocs.org/projects/gsheet-keyring/badge/?version=latest
    :target: http://gsheet-keyring.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. |License| image:: https://img.shields.io/pypi/l/gsheet-keyring.svg
    :target: https://pypi.python.org/pypi/gsheet-keyring
    :alt: License
.. |Supported Python| image:: https://img.shields.io/pypi/pyversions/gsheet-keyring.svg
    :target: https://pypi.python.org/pypi/gsheet-keyring
    :alt: Supported Python Versions

.. _API documentation: http://ipython-secrets.readthedocs.io/en/latest/?badge=latest
.. _Google Colaboratory: https://colab.research.google.com/
.. _Google Sheet key: https://webapps.stackexchange.com/questions/74205/what-is-the-key-in-my-google-sheets-url
.. _gspread: https://gspread.readthedocs.io/en/latest/#gspread.models.Worksheet
.. _ipython-secrets: https://github.com/osteele/ipython-secrets
.. _Keyring API: https://keyring.readthedocs.io/en/latest/?badge=latest#api-interface
.. _Keyring: https://pypi.python.org/pypi/keyring
.. _platform-specific backends: https://pypi.org/project/keyring/#what-is-python-keyring-lib
.. _third-party backends: https://pypi.org/project/keyring/#third-party-backends
