GEMET
=====

.. contents ::

Project Name
------------
The Project Name is GEMET - GEneral Multilingual Environmental Thesaurus
http://www.eionet.europa.eu/gemet

Prerequisites - System packages
-------------------------------

These packages should be installed as superuser (root).

Debian based systems
~~~~~~~~~~~~~~~~~~~~
Install these before setting up an environment::

    apt-get install python-setuptools python-dev libmysqlclient-dev \
    libldap2-dev python-virtualenv mysql-server git


RHEL based systems
~~~~~~~~~~~~~~~~~~
Install Python2.7 with PUIAS: https://gist.github.com/nico4/9616638

Run these commands::

    curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python2.7 -
    pip2.7 install virtualenv
    yum install mysql-server mysql git mysql-devel


Product directory
-----------------

Create the product directory::

    mkdir -p /var/local/gemet
    mkdir /var/local/gemet/logs

Create a new user::

    adduser edw

Change the product directory's owner::

    chown edw:edw /var/local/gemet -R


Install dependencies
--------------------
We should use Virtualenv for isolated environments. The following commands will
be run as an unprivileged user in the product directory::

1. Clone the repository::

    git clone https://github.com/eaudeweb/gemet -o origin gemet
    cd gemet

2.1. Create & activate a virtual environment::

    virtualenv --no-site-packages sandbox
    echo '*' > sandbox/.gitignore
    source sandbox/bin/activate

2.2 Make sure setuptools >= 0.8 is installed::

    pip install -U setuptools

3. Install dependencies::

    pip install -r requirements-dep.txt

4. Create a local configuration file::

    cd gemet
    cp local_settings.py.example local_settings.py

    # Follow instructions in local_settings.py to adapt it to your needs.

6. Set up the MySQL database::

    # Replace [user] and [password] with your MySQL credentials and [db_name]
    # with the name of the database:

    mysql -u[user] -p[password] -e 'create database [db_name] CHARACTER SET
    utf8 COLLATE utf8_general_ci;'

   **The database charset MUST be utf8.**

7. Update local configuration file with database credentials and database name
   - ``default`` section in ``DATABASES`` dict.

8. Create initial database structure::

    ./manage.py syncdb

9. Load fixtures data into the database::

   ./manage.py loaddata gemet/thesaurus/fixtures/data.json

9. Import data, see `Data Import`_ below.

.. _`Data Import`: https://github.com/eaudeweb/gemet#data-import

10. Insert data that enables search to work properly::

    ./manage.py insertdata


Build production
----------------

Setup production environment using an unprivileged user::

    cd /var/local/gemet
    source sandbox/bin/activate

Change the local_settings.py file by setting debug mode off::

    DEBUG = False
    ALLOWED_HOSTS = ['localhost']  # Add allowed hosts to the list as needed

Configure supervisord and set the WSGI server port::

    cp gemet/supervisord.conf.example supervisord.conf
    supervisorctl reload 1>/dev/null || ./bin/supervisord


Build staging
-------------

Setup staging environment using an unprivileged user::

    cd /var/local/gemet
    source sandbox/bin/activate

Change the local_settings.py file by setting debug mode off::

    DEBUG = False
    ALLOWED_HOSTS = ['localhost']  # Add allowed hosts to the list as needed

Configure supervisord and set the WSGI server port (a different one from the
production, for example 8010)::

    cp gemet/supervisord.conf.example supervisord.conf
    supervisorctl reload 1>/dev/null || ./bin/supervisord


Configuration
-------------

Details about configurable settings can be found in ``settings.py``.


Data Import
-----------

1. Considering you have a dump of the old database (``gemet.sql``), import it in a
seaparate database::

    mysql -u[user] -p[password] -e 'create database [db_name] CHARACTER SET utf8 COLLATE utf8_general_ci;'
    mysql [db_name] < gemet.sql

2. Update the ``import`` section from ``DATABASES`` dict in the local
configuration file with the name of the database used for import
(``gemet_old`` from the previous example).

3. Run the management command for data import::

    ./manage.py import


Development hints
=================

Requirements
------------
These packages should be installed as superuser(root)::

    apt-get install libxml2-dev libxslt1-dev

Use ``requirements-dev.txt`` instead of ``requirements-dep.txt``::

    pip install -r requirements-dev.txt

Configure deploy
----------------

* copy ``fabfile/env.ini.example`` to ``fabfile/env.ini``
* configure staging and production settings
* run ``fab staging deploy`` or ``fab production deploy``

Running unit tests
------------------

1. For the GEMET web application::

    ./manage.py test

2. For the API::

    python apitests/api_tests.py

An optional ``--public`` parameter exists, which runs the tests
against the production website.


Contacts
========

The project owner is Søren Roug (soren.roug at eaa.europa.eu)

Other people involved in this project are:

* Cornel Nițu (cornel.nitu at eaudeweb.ro)
* Alex Eftimie (alex.eftimie at eaudeweb.ro)
* Mihai Tabără (mihai.tabara at eaudeweb.ro)
* Iulia Chiriac (iulia.chiriac at eaudeweb.ro)
* Mihai Zamfir (mihai.zamfir at eaudeweb.ro)


Resources
=========

Hardware
--------
Minimum requirements:
 * 2048MB RAM
 * 2 CPU 1.8GHz or faster
 * 4GB hard disk space

Recommended:
 * 4096MB RAM
 * 4 CPU 2.4GHz or faster
 * 8GB hard disk space


Software
--------
Any recent Linux version, apache2, MySQL server, Python 2.7


Copyright and license
=====================

This project is free software; you can redistribute it and/or modify it under
the terms of the EUPL v1.1.

More details under `LICENSE.txt`_.

.. _`LICENSE.txt`: https://github.com/eaudeweb/gemet/blob/master/LICENSE.txt
