"""An example of the gsheet_keyring API.

.. start-include

This example file depends on the presence of a `GOOGLE_APPLICATION_CREDENTIALS`
variable, as described in `Getting Started with Authentication
<https://cloud.google.com/docs/authentication/getting-started>`_.

See `the gspread wiki
<https://github.com/burnash/gspread/wiki/Using-OAuth2-for-Authorization>`_ for
additional information on getting started with Google Authentication.

If you use gsheet-keyring from Google Colaboratory, Google Compute Engine, or
`certain other Google hosting services
<https://cloud.google.com/docs/authentication/production#obtaining_credentials_on_compute_engine_kubernetes_engine_app_engine_flexible_environment_and_cloud_functions>`_,
you don't need to obtain a credentials file. In these cases, you can instantiate
:class:`GoogleSheetKeyring` without a ``credentials`` argument.

.. end-include
"""
import os
import sys

import keyring

from gsheet_keyring import GoogleSheetKeyring
from oauth2client.service_account import ServiceAccountCredentials

try:
    GOOGLE_APPLICATION_CREDENTIALS = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
except KeyError:
    sys.stdout.write("Error: GOOGLE_APPLICATION_CREDENTIALS is not set.\n")
    sys.stdout.write("See the %s module documentation." % __file__)
    sys.exit(1)
scope = ['https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    GOOGLE_APPLICATION_CREDENTIALS, scope)

keyring.set_keyring(GoogleSheetKeyring(credentials=credentials))

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
