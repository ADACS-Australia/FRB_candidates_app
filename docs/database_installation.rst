Database Installation
=====================

Dependancies
------------

For Ubuntu or Debian Linux:

.. code-block::

   sudo apt-get update
   sudo apt-get install postgresql postgresql-contrib libpq-dev python3-dev graphviz python3-pip

Then install the python requirements (recommended in its own virtual environment) using:

.. code-block::

   pip install -r frb_cand/requirements.txt

Environment Variables
---------------------

To run the web application, you will need to set the following environment variables:

.. csv-table::
   :header: "Variable","Description"

   "DB_USER","Postgres user name which you will set in the next section."
   "DB_PASSWORD","Postgres password which you will set in the next section."
   "DB_SECRET_KEY", "Django secret key. `Here <https://saasitive.com/tutorial/generate-django-secret-key/>`_ is a description of how to generate one."
   "SYSTEM_ENV", "Set this either to 'PRODUCTION' to turn off debug and enable CSRF_COOKIE_SECURE, or 'DEVELOPMENT' to turn on debug"
   "UPLOAD_USER", "A username of an account that will be used by upload_xml.py to upload VOEvents"
   "UPLOAD_PASSWORD", "The password of the upload user"


Start the Postgres Database
---------------------------

The following commands will set up the Postgres database for the web app. Replace $DB_USER and $DB_PASSWORD with the environment variable values.

.. code-block::

   sudo -u postgres psql

   CREATE DATABASE frb_cand_db;
   CREATE USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASSWORD';

   ALTER ROLE $DB_USER SET client_encoding TO 'utf8';
   ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';
   ALTER ROLE $DB_USER SET timezone TO 'UTC';


.. _create_database:

Setup database for the first time
---------------------------------

Run the following commands from the webapp_tracet subdirectory so Django can setup up the database structure and upload defaults

.. code-block::

   python manage.py migrate
   python manage.py migrate --run-syncdb


Create a superuser
-------------------

These commands will set up a superuser account.

.. code-block::

   python manage.py createsuperuser


Delete Postgres Database
------------------------

Only do this is you want to restart the database!

To delete the database use the following commands

.. code-block::

   sudo -u postgres psql

   DROP DATABASE frb_cand_db;
   CREATE DATABASE frb_cand_db;

You will then have to recreate the database using the commands in :ref:`create_database`
