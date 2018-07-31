Installing
==========

Paw runs on Python 3 and is tested on versions 3.5.5 and 3.6.6.

It also dependends on Pip to install the project dependencies.

There's pre-defined ways to install Paw for each environment:


Production:

.. code-block:: sh

    $ make install

Development:

.. code-block:: sh

    $ make install-dev

Test:

.. code-block:: sh

    $ make install-test

After install the dependencies and the application, you need to run the migrations in order to create the database tables:

.. code-block:: sh

    $ make migrate

This is it. Everything is installed and should be ready to run now.

A extra step is to load some pre-defined data. This will create the admin user and load range of time and values:

.. code-block:: sh

    $ make load-initial-data

If you are developing new features and changed the models, there's a Makefile target to generate Django automatic migration:

.. code-block:: sh

    $ make migrations

If you need to create a super user, there's the target:

.. code-block:: sh
    
    $ make superuser
