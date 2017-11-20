Magnivore
#########
|Pypi| |Travis|

A data migration tool built to make migrating entire databases as simple as
writing json migration rules.
MySQL, Sqlite and Postgres are supported.

A quick look
------------
A simple migration rule::

    {
        "profiles": {
            "joins": [
                {"table": "users"},
                {"table": "addresses", "on":"user"}
            ],
            "transform": {
                "name": "username",
                "city": "addresses.city"
            }
        }
    }

This would migrate data to the profiles table, using data from users and joined
addresses. In the transform section, we specify which fields we actually want
to migrate.

In this case *users.username* would be migrated to *name* and *addresses.city*
to *city*.

Installing
##########

1. Ensure that you have the necessary database drivers. You will need
   psycopg for postgres and PyMySQL for MySql

2. Install from pip::

    pip install magnivore

3. Configure magnivore. You can generate a skeleton config file with::

    magnivore config-skeleton

3. Initialize magnivore::

    magnivore init

4. Say hello::

    magnivore hello

You have successfully installed magnivore! You can now write migration rules and
execute them with::

    magnivore run myrules.json

Documentation
#############

You can find the full documentation at http://magnivore.readthedocs.io

Troubleshooting
###############

Currently there is poor support for table names that contain dashes, so ensure
that your table names have no dashes.

.. |Pypi| image:: https://img.shields.io/pypi/v/magnivore.svg?maxAge=3600&style=flat-square
   :target: https://pypi.python.org/pypi/magnivore

.. |Travis| image:: https://img.shields.io/travis/wearewhys/magnivore.svg?style=flat-square
    :target: https://travis-ci.org/wearewhys/magnivore
