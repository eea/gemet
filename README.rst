GEMET
=====

.. image:: https://coveralls.io/repos/github/eea/gemet/badge.svg?branch=master
    :target: https://coveralls.io/github/eea/gemet?branch=master

.. image:: https://travis-ci.org/eea/gemet.svg?branch=master
    :target: https://travis-ci.org/eea/gemet

.. image:: https://dockerbuildbadges.quelltext.eu/status.svg?organization=eeacms&repository=gemet
    :target: https://hub.docker.com/r/eeacms/gemet/builds

.. contents ::

Project Name
############
The Project Name is GEMET - GEneral Multilingual Environmental Thesaurus
http://www.eionet.europa.eu/gemet

Installing with Docker
#########################

Create settings files from .example files:

    cp gemet/local_settings.py.example gemet/local_settings.py
    cp gemet/local_test_settings.py.example gemet/local_test_settings.py

Install Docker and docker-compose, then run:

    docker-compose up -d

Now you should be able to attach to the app container:

    docker exec -it gemet.app bash

And run the Django server for development:

    python manage.py runserver 0:8888

Installing without Docker
#########################

Prerequisites - System packages
-------------------------------

These packages should be installed as superuser (root).

Debian based systems
~~~~~~~~~~~~~~~~~~~~
Install these before setting up an environment::

    apt-get install python-setuptools python-dev \
    libldap2-dev python-virtualenv git


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

    git clone https://github.com/eea/gemet -o origin gemet
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

6. Set up the Postgres database::

    # Replace [user] and [password] with your Postgres credentials and [db_name]
    # with the name of the database:

    psql -U[user]
    >> CREATE DATABASE [db_name] CHARACTER SET utf8 COLLATE utf8_general_ci;'

   **The database charset MUST be utf8.**

7. Update local configuration file with database credentials and database name

   - ``default`` section in ``DATABASES`` dict.

8. Create initial database structure::

    ./manage.py migrate

9. Load fixtures data into the database::

   ./manage.py loaddata gemet/thesaurus/fixtures/data.json

10. Generate EIONET static templates::

    ./manage.py fetchtemplates

11. Import data, see `Data Import`_ below.

.. _`Data Import`: https://github.com/eea/gemet#data-import


Build production
################

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
#############

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
#############

Details about configurable settings can be found in ``settings.py``.


Data Import
###########

1. Considering you have a dump of the old database (``gemet.sql``), import it in a
**separate** database::

    psql -U[user] [db_name] < gemet.sql

2. Update the ``import`` section from ``DATABASES`` dict in the local
configuration file with the name of the database used for import
(``gemet_old`` from the previous example).

3. Run the management command for data import::

    ./manage.py import

4. Fix romanian characters::

    ./manage.py fix_romanian

5. Insert data that enables search to work properly::

    ./manage.py insertdata

6. Create reversed relations for all concepts::

    ./manage.py fixrelations

7. Import new terms from the spreadsheet::

    ./manage.py importspreadsheet [spread_sheet_name]


Other commands
##############

1. Some romanian terms, definitions etc. are written with the wrong diacritical marks (cedillas instead of commas).
The following custom management command fixes those characters and prints the number of objects changed::

    ./manage.py fix_romanian


2. Check the consistency of an excel file (.xlsx extension) containing new terms.

The custom command assures:

* Old terms used in the file are defined in the database.
* New terms used in broader, narrow relations etc. of other terms are also defined in the file.
* An error containing the cell of the term is printed if it does not respect those rules.

Run the command providing a valid excel file::

     ./manage.py check_spreadsheet file_name.xlsx


Documentation
#############

The documentation has been created using `Sphinx`_. The source directories for the three sections of documentation can be found in the `docs`_ directory.

.. _`Sphinx`: http://www.sphinx-doc.org/en/stable/
.. _`docs`: https://github.com/eea/gemet/tree/master/docs

In order to get the HTML output, you should run the following command inside one of the documentation directories (``api``, ``new_api`` or ``overview``)::

    make html

These static HTML files can be served via a web server (Apache, Nginx, etc).

Docs contents
~~~~~~~~~~~~~

* ``api`` - old version of the API user guide, kept for reference;
* ``new_api`` - current documentation for the GEMET API; duplicated in `this file`_ and published on ``Web services`` page;
* ``overview`` - quick overview of the technical solution;

.. _`this file`: https://github.com/eea/gemet/blob/master/gemet/thesaurus/templates/api.html


Development hints
=================

Requirements
------------
These packages should be installed as superuser(root)::

    apt-get install libxml2-dev libxslt1-dev

Use ``requirements-dev.txt`` instead of ``requirements-dep.txt``::

    pip install -r requirements-dev.txt


Running unit tests
------------------

0. Before running the tests make sure you have configured the test database
parameters::

    cd gemet/
    cp test_settings.py.example test_settings.py

    # Parameters values should match the ones used for the 'default' database
    # entry in local_settings.py

1. For the GEMET web application::

    ./manage.py test

2. For the API::

    python apitests/main.py

Two optional parameters exist:

* ``--public``, which runs the tests against the production website;
* ``--get``, which calls the API methods through GET requests.

3. Running tests with coverage measurement

Add to your local_settings.py TEST_RUNNER and NOSE_ARGS from
local_settings.example and run::

    ./manage.py test


Sentry settings
===============

Sentry is used to track errors in real-time.

Create an account and a project on `Sentry`_ .

Install the proper version of raven used by sentry::

    pip install -r requirements-dep.txt

Configure local settings with your project's dsn.

.. _`Sentry`: https://sentry.io


Contacts
========

The project owner is Søren Roug (soren.roug at eaa.europa.eu)

Other people involved in this project are:

* Iulia Chiriac (iulia.chiriac at eaudeweb.ro)
* Andrei Melis (andrei.melis at eaudeweb.ro)
* Diana Boiangiu (diana.boiangiu at eaudeweb.ro)
* Cornel Nițu (cornel.nitu at eaudeweb.ro)
* Alex Eftimie (alex.eftimie at eaudeweb.ro)
* Mihai Tabără (mihai.tabara at eaudeweb.ro)
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
Any recent Linux version, apache2, Postgres server, Python 3.8


Copyright and license
=====================

This project is free software; you can redistribute it and/or modify it under
the terms of the EUPL v1.1.

More details under `LICENSE.txt`_.

.. _`LICENSE.txt`: https://github.com/eea/gemet/blob/master/LICENSE.txt
