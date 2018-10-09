bravado_core documentation
==========================

bravado_core is a Python library that implements the `Swagger 2.0 <https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md>`_ Specification.

Client and servers alike can use bravado_core to implement these features:

* Swagger Schema ingestion and validation
* Validation and marshalling of requests and responses
* Validation and marshalling of user-defined Swagger formats
* Modelling Swagger `#/definitions` as Python classes or dicts

For example:

* `bravado <http://github.com/Yelp/bravado>`_ uses bravado-core to implement a fully functional Swagger client.
* `pyramid_swagger <http://github.com/striglia/pyramid_swagger>`_ uses bravado-core to seamlessly add Swagger support to Pyramid webapps.

Contents:

.. toctree::
   :maxdepth: 1

   config
   models
   formats
   changelog


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

