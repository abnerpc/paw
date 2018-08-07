.. Paw documentation master file, created by
   sphinx-quickstart on Sat Jul 28 00:24:48 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Paw's documentation!
===============================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Paw is an application which calculate duration and cost of a phone call based on call events. It provides an API to send the start and end events of a call.

Using a simple admin you can configure the rate minute and standing costs based on range of times.

The API also has an endpoint which returns the phone bill for a given period.

Dependencies
------------

External software dependencies:

Postgres
   Used to store all the data

Redis
   Used as a cache database and as a queue for background worker.

Third part libs:

Django
   Used for the admin, routes and database operations

restless
   Used for easily handle REST calls

rq
   Used as a queue/worker to postpone operations


Contents
--------

.. toctree::
  :maxdepth: 2

  installing
  running
  pawadmin
  modules
  usage

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
