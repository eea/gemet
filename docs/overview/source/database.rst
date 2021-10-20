Database
========

Diagram
-------

The following picture depicts the database diagram, which consists of the
tables in the database, the relationships between them and the columns in each
table with its associated type.

.. figure:: _static/db_diagram.svg
   :alt: Database Diagram

   Database Diagram

Backend
-------

The application uses a single database on a Postgres server running on localhost.
Each table has a corresponding class in ``models``, and the rows in the table
are instances of that class.

Given that concepts are divided into categories according to the namespace they
belong to, five subclasses (of ``Concept``) have been defined: ``Term``,
``Theme``, ``Group``, ``SuperGroup`` and ``Inspire Theme``. These subclasses
are implemented using  ProxyModels_, meaning that any subclass instance is
saved into ``Concept`` database table, and the difference between these is the
Model Manager. Each one of these proxies has a different ``ConceptManager``
instance, which allows to query the ``Concept`` database table only for a
specific subclass (Proxy).
Also dividing the ``Concept`` in five subclasses helps to easily diferentiate
namespace specific operations and to make code more readable.

An important change that has occured as a result of the old database's
remodeling is that the ``value`` column in the ``Property`` table modified its
type from ``TEXT`` to ``VARCHAR(16000)``. The new data type allowed us to index
this column in order to speed up the queries. The length of this column has
been computed by taking into consideration the fact that the maximum row size
in Postgres (the database originally used for the application, is 65,535 bytes
(shared among all columns) and an UTF-8 character uses up to 3 bytes.

Also, the search algorithm has suffered some changes. A new property type,
``searchText``, was introduced; each concept has a property with
``name='searchText'`` and a value obtained by concatenating all of the
properties' values used in search (``prefLabel``, ``hiddenLabel``, ``altLabel``,
``notation``). Therefore, the algorithm will search for a match in the columns
with ``name='searchText'`` of the ``Properties`` table.


.. _ProxyModels: https://docs.djangoproject.com/en/dev/topics/db/models/#proxy-models
