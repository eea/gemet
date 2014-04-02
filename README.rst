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

    TODO


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

    pip install -r requirements.txt

4. Create a configuration file::

    cd gemet
    cp settings.py.example settings.py

6. Set up the MySQL database::

    TODO

7. Create initial database:

    ./manage.py syncdb


Build production
----------------

Setup the production environment like this (using an unprivileged user)::

    TODO

Configure supervisord and set the WSGI server port (by default it is 5000)::

    TODO

At this stage, the application is up and running. You should also configure:

    TODO


Build staging
-------------

    TODO


Configuration
-------------
Details about configurable settings can be found in `settings.py.example`.

    TODO


Data Import
-----------

    TODO


Development hints
=================

Requirements
------------

    TODO

Configure deploy
----------------

    TODO

Running unit tests
------------------

    TODO


Contacts
========

The project owner is Søren Roug (soren.roug at eaa.europa.eu)

Other people involved in this project are:

* Cornel Nițu (cornel.nitu at eaudeweb.ro)
* Alex Eftimie (alex.eftimie at eaudeweb.ro)
* Mihai Tabără (mihai.tabara at eaudeweb.ro)
* Iulia Chiriac (iulia.chiriac at eaudeweb.ro)


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
Any recent Linux version.
apache2, local MySQL server


Copyright and license
=====================

This project is free software; you can redistribute it and/or modify it under
the terms of the EUPL v1.1.

More details under `LICENSE.txt`_.

    TODO
