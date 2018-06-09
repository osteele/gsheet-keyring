Google Sheet Keyring back end
=============================

|PyPI version| |Doc Status| |License| |Supported Python|

This package provides a Keyring_ back end that stores passwords in a Google
Sheet. It was created for use with the ipython-secrets_ package, that uses
Kerying to store secrets that are used in a Jupyter notebook. This package
extends ipython-secret’s functionality, to enable it to be used in Colaboratory_
notebooks, and other hosted services that don’t support the standard Keyring
back ends.

The Python Keyring_ package is a cross-platform password storage library, that
supports a variety of `platform-specific back ends`_, as well as a few
`third-party back ends`_.

None of these other back ends is compatible with Google Colaboratory. (They may
not be compatible with other Jupyter hosting services such as Azure or CoCalc,
either.)

To use this package, simply install it via
``pip3 install gsheet-keyring``, and use the Keyring API as normal. If
one of the built-in Keyring back ends is available, Keyring will use
that. If a platform-specific back end is not available, Keyring will
automatically detect and use this package instead.

To force Keyring to use this package even if other back ends are
available:

.. code:: python

   import keyring
   from gsheet_keyring import GoogleSheetKeyring
   keyring.set_keyring(GoogleSheetKeyring())

By default, this searches for a Google Sheet named “keyring”. If there’s
no sheet with this name, it creates one.

As an alternative, you can also specify a different Google Sheet name, a `Google
Sheet key`_, or a `gspread Worksheet`_. See this package's `API documentation`_
for details on how to do this.

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
.. _ipython-secrets: https://github.com/osteele/ipython-secrets
.. _platform-specific back ends: https://pypi.org/project/keyring/#what-is-python-keyring-lib
.. _third-party back ends: https://pypi.org/project/keyring/#third-party-backends
.. _Google Sheet key: https://webapps.stackexchange.com/questions/74205/what-is-the-key-in-my-google-sheets-url
.. _gspread Worksheet: https://gspread.readthedocs.io/en/latest/#gspread.models.Worksheet
.. _API documentation: http://ipython-secrets.readthedocs.io/en/latest/?badge=latest
