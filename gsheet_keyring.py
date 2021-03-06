"""This package provides a Keyring backend that is backed by a Google Sheet.

Example
=======

:download:`example.py <./example.py>` is an example of using this package
outside of Google Colaboratory, Google Compute Engine, or another environment
that sets Google OAuth2 credentials automatically.

.. include:: credentials.rst
.. include:: caching.rst
.. include:: cautions.rst
.. include:: links.rst
"""

import os
import time
from datetime import datetime
from functools import lru_cache

import gspread
import keyring
from keyring.errors import InitError, PasswordDeleteError
from oauth2client.client import ApplicationDefaultCredentialsError, GoogleCredentials
from oauth2client.service_account import ServiceAccountCredentials

__version__ = '1.0.1'

SERVICENAME_COL = 1
USERNAME_COL = 2
PASSWORD_COL = 3
CREATED_AT_COL = 4
UPDATED_AT_COL = 5


class GoogleSheetKeyring(keyring.backend.KeyringBackend):
    """A Keyring back end backed by a Google Sheet."""

    _sheet_key = None
    _sheet_title = 'keyring'
    _sheet_url = None
    _worksheet = None
    _credentials = None
    _cache_renewal_seconds = 60
    __cache = None
    __cache_accessed_at = 0

    priority = 0.5

    def __init__(self, *, sheet_key=None, sheet_title='keyring', sheet_url=None,
                 credentials=None, worksheet=None):
        """Initialize a :class:`GoogleSheetKeyring`.

        The Google Sheet may be specified with a variety of parameters. They
        have the precedence `worksheet` > `sheet_url` > `sheet_key` >
        `sheet_title`. The first truthy parameter is used. Lower-precedence
        parameters are silently ignored. For example, if `sheet_url` is truthy,
        `sheet_key` and `sheet_title` are ignored. If the only truthy parameter
        is `sheet_title` and no sheet with this title is found, a new sheet is
        created. This is in the only circumstance in which this class will
        create a new sheet.

        Parameters
        ----------
        credentials : :class:`oauth2client.client.GoogleCredentials`, optional
            An instance of :class:`oauth2client.client.GoogleCredentials`.
        sheet_key : str, optional
            A `Google Sheet document key`_.
        sheet_title : str, optional
            A Google Sheet document title. Defaults to ``"keyring"``.
        sheet_url : str, optional
            A Google Sheet document URL.
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
    @lru_cache(maxsize=1)
    def credentials(self):
        """Return an instance of :class:`oauth2client.client.GoogleCredentials`.

        This has the value of the ``credentials`` initialization parameter.

        If this parameter isn't specified, the credentials are computed as
        described in the module documentation.
        """
        if self._credentials:
            return self._credentials
        credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if credentials_path:
            scope = ['https://www.googleapis.com/auth/drive']
            return ServiceAccountCredentials.from_json_keyfile_name(
                credentials_path, scope)
        try:
            return GoogleCredentials.get_application_default()
        except ApplicationDefaultCredentialsError as err:
            try:
                from google.colab import auth
                auth.authenticate_user()
                return GoogleCredentials.get_application_default()
            except ImportError:
                raise err

    @property
    @lru_cache(maxsize=1)
    def sheet(self):
        """Return the backing store :class:`gspread.models.Worksheet`."""
        if self._worksheet:
            return self._worksheet
        key = self._sheet_key
        title = self._sheet_title
        url = self._sheet_url
        gc = gspread.authorize(self.credentials)
        if key:
            try:
                doc = gc.open_by_key(key)
            except gspread.SpreadsheetNotFound:
                raise InitError('Spreadsheet not found')
        elif url:
            try:
                doc = gc.open_by_url(url)
            except gspread.SpreadsheetNotFound:
                raise InitError('Spreadsheet not found')
        else:
            try:
                doc = gc.open(title)
            except gspread.SpreadsheetNotFound:
                doc = gc.create(title)
            except gspread.exceptions.APIError as e:
                raise InitError(e)
        return doc.sheet1

    @property
    def _cache(self):
        now = time.time()
        if now > self.__cache_accessed_at + self._cache_renewal_seconds:
            self.__cache = dict()
        self.__cache_accessed_at = now
        return self.__cache

    def _current_time(self):
        """Return the current time, formatted for Google Sheets.

        Get the current time formatted s.t Google Sheets recognizes it as a
        datetime.

        Google Sheets doesn't recognize datetime formats with timezones. We use
        UTC, but this isn't indicated in the data.
        """
        dt = datetime.utcnow()
        return dt.strftime('%Y-%m-%d %H:%M')

    def _find_rows(self, servicename, username):
        """Get a set of row numbers that match the provided servicename and username."""
        ws = self.sheet
        servicename_rows = {c.row for c in ws.findall(servicename)
                            if c.col == SERVICENAME_COL}
        username_rows = {c.row for c in ws.findall(username)
                         if c.col == USERNAME_COL}
        return servicename_rows & username_rows

    def set_password(self, servicename, username, password):
        """Set password for the username of the service."""
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
        """Get password of the username for the service."""
        cache_key = (servicename, username)
        if cache_key in self._cache:
            return self._cache[cache_key]
        rows = self._find_rows(servicename, username)
        password = (self.sheet.cell(min(rows), PASSWORD_COL).value
                    if rows else None)
        self._cache[cache_key] = password
        return password

    def delete_password(self, servicename, username):
        """Delete the password for the username of the service."""
        ws = self.sheet
        rows = self._find_rows(servicename, username)
        if not rows:
            raise PasswordDeleteError("Password not found")
        # There can be multiple matching rows if the sheet has been
        # manually edited or there's been a race.
        for r in sorted(rows)[::-1]:
            ws.delete_row(r)
        self._cache.pop((servicename, username), None)
