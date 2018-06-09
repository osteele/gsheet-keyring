"""This package provides a Keyring back end backed by a Google Sheet.

It was created for use with the ipython-secrets_ package, that uses Keyring_ to
store secrets that are used in a Jupyter notebook. This package extends
ipython-secret's functionality, to enable it to be used in Colaboratory
notebooks, and with other hosted services that don't support the standard
Keyring back ends.

Example
=======

:download:`example.py <./example.py>` is an example of using this package
outside of Google Colaboratory, Google Compute Engine, or another environment
that sets Google OAuth2 credentials automatically.

.. include:: example.py
   :start-after: start-include
   :end-before: end-include

.. _Keyring: https://pypi.python.org/pypi/keyring
.. _ipython-secrets: https://github.com/osteele/ipython-secrets

Caching
=======

Access to Google Sheets is very slow. This package performs minimal caching —
just enough to optimize these cases:

-  The caller sets and then gets a password.
-  The caller gets a password multiple times.

In order to minimize the risk of using stale data when a notebook is left
running in a background browser tab while you interact with another tab. The
cache expires quickly. [#f1]_

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

.. rubric:: Footnotes

.. [#f1] Data is currently cached for a minute, counting from the last access
  (to any password, not just the requested password). This is slow by Python
  execution speed, but fast by human standards. This matches the intended use
  of the package.
"""

from datetime import datetime
import time

import keyring
from keyring.errors import InitError, PasswordDeleteError

import gspread
from oauth2client.client import GoogleCredentials

__version__ = '0.1.2'

SERVICENAME_COL = 1
USERNAME_COL = 2
PASSWORD_COL = 3
CREATED_AT_COL = 4
UPDATED_AT_COL = 5


class GoogleSheetKeyring(keyring.backend.KeyringBackend):
    """A Keyring back end backed by a Google Sheet.
    """

    _sheet_key = None
    _sheet_title = 'keyring'
    _sheet_url = None
    _worksheet = None
    _credentials = None
    _cache_renewal_seconds = 60
    __cache = None
    __cache_accessed_at = 0

    priority = 0.5

    def __init__(self, *, sheet_key='keyring', sheet_title=None, sheet_url=None,
                 credentials=None, worksheet=None):
        """
        The Google Sheet may be specified with a variety of parameters. They
        have the precedence `worksheet` > `sheet_url` > `sheet_key` >
        `sheet_title`. The first truthy parameter is used. Lower-precedence
        parameters are silently ignored. For example, if `sheet_url` is truthy,
        `sheet_key` and `sheet_title` are ignored. If the only truthy parameter
        is `sheet_title` and no sheet with this title is found, a new sheet is
        created. This is in the only circumstance in which this class will
        create a new sheet.

        .. _Google Sheet key: https://webapps.stackexchange.com/questions/74205/what-is-the-key-in-my-google-sheets-url

        Parameters
        ----------
        credentials : :class:`oauth2client.client.GoogleCredentials`, optional
            An instance of :class:`oauth2client.client.GoogleCredentials`.
        sheet_key : str, optional
            A `Google Sheet key`_.
        sheet_title : str, optional
            A Google Sheet document title. Defaults to ``"keyring"``.
        worksheet : :class:`gspread.models.Worksheet`, optional
            A :class:`gspread.models.Worksheet` instance.
        """
        super().__init__()
        self._sheet_key = sheet_key
        self._sheet_title = sheet_title
        self._sheet_url = sheet_url
        self._worksheet = worksheet
        self._credentials = credentials

    @property
    def credentials(self):
        """An instance of :class:`oauth2client.client.GoogleCredentials`."""
        if not self._credentials:
            self._credentials = GoogleCredentials.get_application_default()
        return self._credentials

    @property
    def sheet(self):
        """The :class:`gspread.models.Worksheet` that is used as a backing
        store."""
        if self._worksheet:
            return self._worksheet
        key = self._sheet_key
        title = self._sheet_title
        gc = gspread.authorize(self.credentials)
        if key:
            try:
                doc = gc.open_by_key(key)
            except gspread.SpreadsheetNotFound:
                raise InitError('Spreadsheet not found')
        else:
            try:
                doc = gc.open(title)
            except gspread.SpreadsheetNotFound:
                doc = gc.create(title)
            except gspread.exceptions.APIError as e:
                raise InitError(e)
        self._worksheet = doc.sheet1
        return self._worksheet

    @property
    def _cache(self):
        now = time.time()
        if now > self.__cache_accessed_at + self._cache_renewal_seconds:
            self.__cache = dict()
        self.__cache_accessed_at = now
        return self.__cache

    def _current_time(self):
        """Get current time formatted s.t Google Sheets recognizes it as a
        datetime.

        Google Sheets doesn't recognize datetime formats with timezones. We use
        UTC, but this isn't indicated in the data.
        """
        dt = datetime.utcnow()
        return dt.strftime('%Y-%m-%d %H:%M')

    def _find_rows(self, servicename, username):
        """Get a set of row numbers that match the provided servicename and username.
        """
        ws = self.sheet
        servicename_rows = {c.row for c in ws.findall(servicename)
                            if c.col == SERVICENAME_COL}
        username_rows = {c.row for c in ws.findall(username)
                         if c.col == USERNAME_COL}
        return servicename_rows & username_rows

    def set_password(self, servicename, username, password):
        """Set password for the username of the service
        """
        ts = self._current_time()
        ws = self.sheet
        cache_key = (servicename, username)
        rows = self._find_rows(servicename, username)
        if rows:
            r = min(rows)
            if ws.cell(min(rows), PASSWORD_COL).value != password:
                ws.update_cell(r, PASSWORD_COL, password)
                cells = ws.range(r, UPDATED_AT_COL, r, UPDATED_AT_COL)
                cells[0].value = ts
                ws.update_cells(cells, value_input_option='USER_ENTERED')
        else:
            # new rows go at the top, right below the header
            r = 2
            ws.insert_row([servicename, username, password], index=r)
            cells = ws.range(r, CREATED_AT_COL, r, UPDATED_AT_COL)
            cells[0].value = ts
            cells[1].value = ts
            ws.update_cells(cells, value_input_option='USER_ENTERED')
        self._cache[cache_key] = password

    def get_password(self, servicename, username):
        """Get password of the username for the service
        """
        cache_key = (servicename, username)
        if cache_key in self._cache:
            return self._cache[cache_key]
        rows = self._find_rows(servicename, username)
        password = (self.sheet.cell(min(rows), PASSWORD_COL).value
                    if rows else None)
        self._cache[cache_key] = password
        return password

    def delete_password(self, servicename, username):
        """Delete the password for the username of the service.
        """
        ws = self.sheet
        rows = self._find_rows(servicename, username)
        if not rows:
            raise PasswordDeleteError("Password not found")
        # There can be multiple matching rows if the sheet has been
        # manually edited or there's been a race.
        for r in sorted(rows)[::-1]:
            ws.delete_row(r)
        self._cache.pop((servicename, username), None)
