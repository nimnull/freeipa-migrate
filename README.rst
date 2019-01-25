FreeIPA backup and migration
============================

Install
-------

Designed to work under the Python 3.7+


.. code-block:: bash

    pip install -e .
    export IPA_HOST="server fqdn/ip"
    export IPA_LOGIN="login"
    export IPA_PASSWORD="password"

    migrate dump dumpfile.db
    migrate restore dumpfile.db

