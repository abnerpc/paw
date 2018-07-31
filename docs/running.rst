Running
=======

To have the full application running you need to run two things. The server wich is responsable for serving the endpoints for the admin and the API. Another thing you need to run is the RQ worker that is responsable to process the job to save the call event and calculate the bill for the end events.

Server
------

To run the server you just need to execute:

.. code-block:: sh

    $ make run

The application needs some environment variables setted in the machine to run. For development purposes, in the first time you run it will copy the file .env from contrib folder, wich contains all the variables required and will be used by the application. You can use this file to run the application in a production environment, but exporting the variables for the environment is a better secutiry approach.

Environment variables required by the application:

* SECRET_KEY
   This is the secret key used by Django application.
* DEBUG
   Indicates to Django to run in Debug mode. Remember to set this to `False` or do not exporting it.
* ALLOWED_HOSTS
   Indicates to Django the hosts allowed. Set as according the server you are running.
* POSTGRES_HOST
   Host address of your Postgres database.
* POSTGRES_USER
   User for the Postgres database created.
* POSTGRES_PASSWORD
   Password for the Postgres User.
* REDIS_RQ_URL
   Host of the Redis server for the RQ queue.
* REDIS_URL
   Host of the Redis server for general cache in the application.


Worker
------

To run the worker which will process the jobs in the RQ queue:

.. code-block:: sh

    $ make worker

Now, the worker will keep running in the background and will process the jobs that come to the RQ queue.

If some job fail, you can view and re-queue the job through the Django admin. This is covered in somewhere.


Tests
-----

If you are in a development environment, it is mandatory that you run the tests for any change you make. When you install the development environment using the target install-dev, it will provide everything you need to run the tests.

To run the tests:

.. code-block:: sh

    $ make test

If you want to follow the coverage of the unit tests:

.. code-block:: sh

    $ make test-cov

The repository also contains a Travis file configuration to run the tests using tox. Tox is used to run the tests in differents versions of python. You can also run it locally but you will need to install the test environment using install-test. After installing the dependencies just hit:

.. code-block:: sh

    $ make test-tox
