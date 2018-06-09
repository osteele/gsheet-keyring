.. caution::

  Passwords are stored *unencrypted* in your Google Sheet. Standard security
  warnings apply:

  -  Don’t share your “keyring” Google Sheet more widely than you want your
     passwords shared.
  -  Anyone with access to your Google account has access to these passwords.

     -  This includes anyone who can sign into a laptop or phone that is signed
        into your Google account.

  -  If you open the spreadsheet in a public place, you are vulnerable to
     shoulder surfing.
  -  If you open it within view of a camera, you have leaked your passwords to
     (today) anyone who can view the stream, or (going forwards) anyone who
     gains access to a server that stores the stream. (Hello, Nest!)
  -  Even if you open the spreadsheet in a private place, you’re only as secure
     as the physical security of the lines of sight (including through windows)
     to your screen.

.. caution::

  This package’s use of Google Sheets is neither `Atomic, nor Consistent, nor
  Isolated <https://en.wikipedia.org/wiki/ACID#Characteristics>`_.

  Simultaneous calls to a single writer (a single call to either
  :func:`~GoogleSheetKeyring.set_password` or
  :func:`~GoogleSheetKeyring.delete_password`) and/or multiple readers
  (any number of calls to :func:`~GoogleSheetKeyring.get_password`) should be
  fine.

  Simultaneous calls (for example, from different Jupyter notebooks) to
  :func:`~GoogleSheetKeyring.set_password` and/or
  :func:`~GoogleSheetKeyring.delete_password` can easily corrupt the
  spreadsheet. If you need this capability, this package (and Google Sheets) is
  not the right technology to build it on top of. In this case, consider using a
  hosted database as a back end, or using a hosted key management service
  instead of Keyring.
