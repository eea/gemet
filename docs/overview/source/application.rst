Application
===========

This application has been developed using the Django web framework and it uses
a Postgres database.

It runs in an isolated environment, using Virtualenv.

Directory structure
-------------------

The root of the project contains the following directories and files:

* **apitests/** - a module used for testing the API
* **docs/** - project documentation including: API documentation, architecture overview, database schema
* **LICENSE.txt** - project's license
* **manage.py** - tool for running Django management commands
* **README.rst** - step-by-step installation tutorial
* **requirements-dep.txt** - packages required in deployment
* **requirements-dev.txt** - packages required in development
* **requirements.txt** - common packages used for both development and deployment
* **gemet/** - application folder
* **sandbox/** - virtualenv folder
* **supervisord.conf.example** - configuration file example for supervisor

The application folder, **gemet**, has a directory structure typical for a Django
project::

    ├── layout.py
    ├── local_settings.py
    ├── settings.py
    ├── test_settings.py
    ├── urls.py
    ├── wsgi.py
    └── thesaurus
        ├── admin.py
        ├── api.py
        ├── collation_charts.py
        ├── fixtures/
        ├── forms.py
        ├── models.py
        ├── static/
        ├── templates/
        ├── templatetags/
        ├── tests/
        ├── urls.py
        ├── utils.py
        ├── views.py
        └── management/
            └── commands/


A few words about the files and directories found in **gemet** folder:

* **layout.py** - middleware component used for plone layout integration
* **local_settigs.py, settings.py, test_settings.py** - settings files
* **thesaurus/** - project module

    * **admin.py** - file that defines entities available in the admin
      interface
    * **api.py** - API module (more about the methods it exposes in the *API
      Documentation*)
    * **collation_charts.py** - map of unicode alphabets for all languages
    * **fixtures/** - initial data for some of the models, stored in JSON
      format
    * **forms.py** - a module containing all the forms used in the application
    * **management/commands/** - custom commands defined for the Django manager
    * **models.py** - database abstraction
    * **static/** - static files (CSS)
    * **templates/** - HTML templates rendered by the views
    * **templatetags/** - custom template tags
    * **tests/** - unit testing for the application
    * **urls.py** - URL configuration
    * **utils.py** - helper functions
    * **views.py** - collection of class-based views (views describe the data
      that gets presented to the user trough the templates)

* **urls.py** - URL configuration
* **wsgi.py** - WSGI configuration
