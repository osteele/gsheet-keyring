Credentials
===========

A :class:`~oauth2client.client.GoogleCredentials` instance is required in order
to access the Google Sheet. This can be supplied in one of the following ways:

1. Follow the instructions in `Getting Started with Authentication
   <https://cloud.google.com/docs/authentication/getting-started>`_.
   Set the ``GOOGLE_APPLICATION_CREDENTIALS`` environment variable to the
   path to the service account key file.
2. If the code is running in Google Compute Engine or `certain other Google
   environments <https://cloud.google.com/docs/authentication/production#obtaining_credentials_on_compute_engine_kubernetes_engine_app_engine_flexible_environment_and_cloud_functions>`_,
   the code uses the instance's service account via
   :func:`oauth2client.client.GoogleCredentials.get_application_default`.
3. If the code is running in a Colaboratory notebook, the user will be asked
   to sign in via :func:`google.colab.auth.authenticate_user`.
4. Use :mod:`~oauth2client` to instantiate a
   :class:`~oauth2client.client.GoogleCredentials`. Pass it as the `credential`
   parameter to :func:`GoogleSheetKeyring`. See `the gspread wiki
   <https://github.com/burnash/gspread/wiki/Using-OAuth2-for-Authorization>`_
   for additional information on getting started with Google Authentication.

If you use gsheet-keyring from Google Colaboratory, Google Compute Engine, or
`certain other Google hosting services
<https://cloud.google.com/docs/authentication/production#obtaining_credentials_on_compute_engine_kubernetes_engine_app_engine_flexible_environment_and_cloud_functions>`_,
you don't need to obtain a credentials file. In these cases, you can instantiate
:class:`GoogleSheetKeyring` without a ``credentials`` argument.
