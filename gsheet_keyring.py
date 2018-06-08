"""This package provides a Keyring_ back end that stores passwords in a Google
Sheet. It was created for use with the ipython-secrets_ package, that uses
Keyring to store secrets that are used in a Jupyter notebook. This package
extends ipython-secret's functionality, to enable it to be used in Colaboratory
notebooks, and with other hosted services that don't support the standard `keyring`
back ends.

.. _Keyring: https://pypi.python.org/pypi/keyring
.. _ipython-secrets: https://github.com/osteele/ipython-secrets
"""

from datetime import datetime
import time

import keyring
from keyring.errors import InitError, PasswordDeleteError

import gspread
from oauth2client.client import GoogleCredentials

__version__ = '0.1.0'

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

    # compute priority dynamically based on import error
    priority = 0.5

    def __init__(self, *, sheet_key=None, sheet_title=None, sheet_url=None,
                 credentials=None, worksheet=None):
        """
        The Google Sheet may be specified with a variety of parameters. They
        have the precedence `worksheet` > `sheet_url` > `sheet_key` >
        `sheet_title`. The first non-falsey parameter is used: lower-precedence
        parameters are silently ignored. If the only non-falsey parameter is
        `sheet_title` and no sheet with this title is found, a new sheet is
        created. This is in the only circumstance in which this class will
        create a new sheet.

        .. _Google Sheet key: https://webapps.stackexchange.com/questions/74205/what-is-the-key-in-my-google-sheets-url
        .. _gspread Worksheet: https://gspread.readthedocs.io/en/latest/#gspread.models.Worksheet

        Parameters
        ----------
        credentials : object
            `oauth2` credentials.
        sheet_key : str
            A `Google Sheet key`_.
        sheet_title : str
            A Google Sheet document title.
        worksheet : :class:`gspread.Worksheet`
            A `gspread Worksheet`_ instance.
        """
        super().__init__()
        self._sheet_key = sheet_key
        self._sheet_title = sheet_title
        self._sheet_url = sheet_url
        self._worksheet = worksheet
        self._credentials = credentials

    @property
    def credentials(self):
        """Google Auth credentials."""
        if not self._credentials:
            self._credentials = GoogleCredentials.get_application_default()
        return self._credentials

    @property
    def sheet(self):
        """The gspread Google Sheet."""
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
