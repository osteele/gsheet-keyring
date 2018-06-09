Caching
=======

Access to Google Sheets is very slow. This package performs minimal caching —
just enough to optimize these cases:

-  The caller sets and then gets a password.
-  The caller gets a password multiple times.

In order to minimize the risk of using stale data when a notebook is left
running in a background browser tab while you interact with another tab. The
cache expires quickly. [#f1]_

.. [#f1] Data is currently cached for a minute, counting from the last access
  (to any password, not just the requested password). This is slow by Python
  execution speed, but fast by human standards. This matches the intended use
  of the package.
