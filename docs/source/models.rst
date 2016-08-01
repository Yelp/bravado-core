.. _models:

Python Models
=============

Models in a Swagger spec are usually defined under the path ``#/definitions``.

A model can refer to a primitive type or a container type such as a ``list`` or
a ``dict``. In ``dict`` form, there is an opportunity to make the interface to
access the properties of a model a little more straight forward.

Consider the following:

.. code-block:: json

    {
        "definitions": {
            "Pet": {
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                    "breed": {"type": "string"}
                }
            }
        }
    }

In python, this model easily maps to a ``dict``:

.. code-block:: python

    pet = {
        "name": "Sumi",
        "age": 12,
        "breed": None,
    }

    print pet['name']

    if pet['age'] < 1:
        print 'What a cute puppy!'

    if pet['breed'] is None:
        pet['breed'] = 'mutt'


However, if the model is implemented as a Python type, dotted access to
properties becomes a reality:

.. code-block:: python

    from bravado_core.spec import Spec

    spec = Spec.from_dict(...)
    Pet = spec.definitions['Pet']
    pet = Pet(name='Sumi', age=12)

    print pet.name

    if pet.age < 1:
        print 'What a cute puppy!'

    if pet.breed is None:
        pet.breed = 'mutt'

Configuring Models as Python Types
----------------------------------
bravado-core supports models as both dicts and python types.

The feature to use python types for models is enabled by default. You can
always disable it if necessary.

.. code-block:: python

    from bravado_core.spec import Spec
    swagger_dict = {..}
    spec = Spec.from_dict(swagger_dict, config={'use_models': False})

Allowing null values for properties
-----------------------------------
Typically, bravado-core will complain during validation if it encounters fields with ``null`` values.
This can be problematic, especially when you're adding Swagger support to pre-existing
APIs. In that case, declare your model properties as ``x-nullable``:

.. code-block:: json

    {
        "Pet": {
            "type": "object",
            "properties": {
                "breed": {
                    "type": "string",
                    "x-nullable": true
                }
            }
        }
    }

Model Discovery
---------------
Keep in mind that bravado-core has to do some extra legwork to figure out which
parts of your spec represent Swagger models and which parts don't to make this
feature work automagically. With a single-file Swagger spec, this is pretty
straight forward - everything under ``#/definitions`` is a model. However, with
more complicated specs that span multiple files and use external refs, it
becomes a bit more involved. For this reason, the discovery process for
models is best effort with a fallback to explicit annotations as follows:

1. Search for refs that refer to ``#/definitions`` in local scope
2. Search for refs that refer to external definitions with pattern ``<filename>#/definitions/<model name>``.

   *swagger.json*

   .. code-block:: json

       {
            "paths": {
                "/pet": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "A pet",
                                "schema": {
                                    "$ref": "another_file.json#/definitions/Pet"
                                }
                            }
                        }
                    }
                }
            }
        }

   *another_file.json*

   .. code-block:: json

       {
           "definitions": {
               "Pet": {
                   ...
               }
           }
       }

3. Search for the ``"x-model": "<model name>"`` annotation to identify models that can't be found via method 1. or 2.

   *swagger.json*

   .. code-block:: json

      {
          "paths": {
              "/pet": {
                  "get": {
                      "responses": {
                          "200": {
                              "description": "A pet",
                              "schema": {
                                  "$ref": "https://my.company.com/definitions/models.json#/models/Pet"
                              }
                          }
                      }
                  }
              }
          }
      }

   *models.json* (served up via ``https://my.company.com/definitions/models.json``)

   .. code-block:: json

       {
           "models": {
               "Pet": {
                    "x-model": "Pet"
                   ...
               }
           }
       }

