Google Sheet Keyring backend
============================

|PyPI version| |Doc Status| |License| |Supported Python|

This package provides a Keyring_ backend that stores passwords in a Google
Sheet. It was created for use with the ipython-secrets_ package, that uses
Kerying to store secrets that are used in a Jupyter notebook. This package
extends ipython-secret’s functionality, to enable it to be used in Colaboratory_
notebooks, and other hosted services that don’t support the standard Keyring
backends.

The Python Keyring package is a cross-platform password storage library, that
supports a variety of `platform-specific backends`_, as well as a few
`third-party backends`_.

None of these other backends is compatible with Google Colaboratory. (They may
not be compatible with other Jupyter hosting services such as Azure or CoCalc,
either.) That's the problem that this package solves.

To use this package, install it via ``pip3 install gsheet-keyring``, and use the
`Keyring API`_ as normal. If one of the built-in Keyring backends is available,
Keyring will use that. If a platform-specific backend is not available, Keyring
will automatically detect and use this package instead.

Use ``keyring.set_keyring`` to force Keyring to use this package even if other
backends are available:

.. code:: python

   import keyring
   from gsheet_keyring import GoogleSheetKeyring
   keyring.set_keyring(GoogleSheetKeyring())

By default, this searches for a Google Sheet named “keyring”. If there’s
no sheet with this name, one is created.

As an alternative, you may also specify a different Google Sheet name, a Google
Sheet key, or a Worksheet from the `gspread`_ package.

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

.. _Colaboratory: https://colab.research.google.com/
.. _Keyring: https://pypi.python.org/pypi/keyring
.. _Keyring API: https://keyring.readthedocs.io/en/latest/?badge=latest#api-interface
.. _ipython-secrets: https://github.com/osteele/ipython-secrets
.. _platform-specific backends: https://pypi.org/project/keyring/#what-is-python-keyring-lib
.. _third-party backends: https://pypi.org/project/keyring/#third-party-backends
.. _Google Sheet key: https://webapps.stackexchange.com/questions/74205/what-is-the-key-in-my-google-sheets-url
.. _gspread: https://gspread.readthedocs.io/en/latest/#gspread.models.Worksheet
.. _API documentation: http://ipython-secrets.readthedocs.io/en/latest/?badge=latest
