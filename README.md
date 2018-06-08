# gsheet_keyring

This package provides a [Keyring](https://pypi.python.org/pypi/keyring) back end
that stores passwords in a Google Sheet. It was created for use with the
[ipython-secrets](https://github.com/osteele/ipython-secrets) package, that uses
Kerying to store secrets that are used in a Jupyter notebook. This package
extends ipython-secret's functionality, to enable it to be used in Colaboratory
notebooks, and other hosted services that don't support the standard `keyring`
back ends.

The Python [keyring package](https://pypi.python.org/pypi/keyring) is a
cross-platform password storage library, that supports a variety of
[platform-specific back
ends](https://pypi.org/project/keyring/#what-is-python-keyring-lib), as well as
a few [third-party back
ends](https://pypi.org/project/keyring/#third-party-backends).

None of these back ends is compatible with the [Google
Colaboratory](https://colab.research.google.com/) hosted Jupyter service. (They
may not be compatible with other hosted Jupyter services such as Azure or
CoCalc, either.)

To use this package, simply install it via `pip install gsheet-keyring`, and use
the Keyring API as normal. If one of the built-in Keyring back ends is
available, Keyring will use that. If a platform-specific back end is not
available, Keyring will automatically detect and use this package instead.

To force Keyring to use this package even if other back ends are available:

```python
from gsheet_keyring import GoogleSheetKeyring
keyring.set_keyring(GoogleSheetKeyring())
```

See <./example.py> for a complete example.

By default, this searches for a Google Sheet named "keyring". If this doesn't
exist, it creates a sheet with this name. As an alternative, you can also
specify a different Google Sheet name, a Google Sheet
[key](https://webapps.stackexchange.com/questions/74205/what-is-the-key-in-my-google-sheets-url),
or a [gspread
`Worksheet`](https://gspread.readthedocs.io/en/latest/#gspread.models.Worksheet).
See the API documentation for more details.

## Cache

Access to Google Sheets is very slow. This package performs minimal caching, to
optimize the cases where the caller sets and then gets a password, or gets a
password multiple times. The cache expires quickly (currently a minute — this is
slow by Python execution speed but fast by human standards, which matches the
intended use of the package), in order to minimize the risk of using stale data
when a notebook is left running in a background browser tab while you interact
with another tab.

## Limitations

This package's use of Google Sheets is neither [Atomic, nor Consistent, nor
Isolated](https://en.wikipedia.org/wiki/ACID#Characteristics).

The concurrent use of a single writer (`set_password`, `delete_password`) and
multiple readers (`get_password`) should be all right.

Concurrent calls (for example, from different Jupyter notebooks) to
`set_password` and/or `delete_password` can easily corrupt the spreadsheet. If
you need this capability, this package (and Google Sheets) is not the right
technology to build it on top of. In this case, consider using a hosted database
as a back end, or using a hosted key management service instead of Keyring.

## Security

Passwords are stored *unencrypted* in your Google Sheet. Standard security
warnings apply:

* Don't share your “keyring” Google Sheet more widely than you want your
  passwords stored.
* Anyone with access to your Google account has access to these passwords.
  * This includes anyone who can sign into a laptop or phone that is signed into
    your Google account.
* If you open this spreadsheet in a public place, you are vulnerable to
  shoulder surfing.
* If you open it within view of a camera, you have leaked your passwords to
  (today) anyone who can view the stream, or (tomorrow) anyone who gains access
  to a server that stores the stream. (Hello, Nest!)
* Even if you open this spreadsheet in a private place, you're only as secure as
  the physical security of the lines of sight (including through windows) to
  your screen.

## License

MIT
