"""An example of the gsheet_keyring API.

This example file depends on the presence of a `GOOGLE_APPLICATION_CREDENTIALS`
variable, as described in `Getting Started with Authentication
<https://cloud.google.com/docs/authentication/getting-started>`_.

See `the gspread wiki
<https://github.com/burnash/gspread/wiki/Using-OAuth2-for-Authorization>`_ for
additional information on getting started with Google Authentication.
"""
import os
import sys

import keyring

from gsheet_keyring import GoogleSheetKeyring

keyring.set_keyring(GoogleSheetKeyring())

keyring.set_password('service1', 'user1', 'secret1')
passwd = keyring.get_password('service1', 'user1')
assert passwd == 'secret1'

keyring.set_password('service1', 'user1', 'secret2')
passwd = keyring.get_password('service1', 'user1')
assert passwd == 'secret2'

keyring.set_password('service1', 'user2', 'secret3')
passwd = keyring.get_password('service1', 'user2')
assert passwd == 'secret3'

keyring.set_password('service2', 'user1', 'secret4')
passwd = keyring.get_password('service2', 'user1')
assert passwd == 'secret4'

keyring.set_password('service1', 'user1', 'secret5')
passwd = keyring.get_password('service1', 'user1')
assert passwd == 'secret5'

keyring.delete_password('service1', 'user1')
passwd = keyring.get_password('service1', 'user1')
assert passwd is None

passwd = keyring.get_password('service1', 'user2')
assert passwd == 'secret3'
