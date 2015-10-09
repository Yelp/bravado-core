.. _formats:

User-Defined Formats
====================

Primitive types in Swagger support an optional modifier property ``format`` as
explained in detail in the `Swagger Specification <https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#data-types>`_.
With this feature, you can define your own domain specific formats and have
validation and marshalling to/from python/json handled transparently.

Creating a user-defined format
------------------------------
This is best explained with a simple example. Let's create a user-defined
format for `CIDR notation <https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing#CIDR_notation>`_.

In a Swagger spec, the schema-object for a CIDR would resemble:

.. code-block:: json

    {
        "type": "string",
        "format": "cidr",
        "description": "IPv4 CIDR"
    }

In python, we'd like CIDRs to automatically be converted to a ``CIDR`` object
that makes them easy to work with.

.. code-block:: python

    class CIDR(object):
        def __init__(self, cidr):
            """
            :param cidr: CIDR in string form.
            """
            self.cidr = cidr

        def overlaps(self, other_cidr):
            """Return true if other_cidr overlaps with this cidr"""
            ...

        def subnet_mask(self):
            """Return the subnet mask of this cidr"""
            ...

        ...

We would also like CIDRs to be validated by bravado-core whenever they are
part of a HTTP request or response.

Create a ``bravado_core.formatter.SwaggerFormat`` to define the CIDR format:

.. code-block:: python

    from bravado_core.formatter import SwaggerFormat

    def validate_cidr(cidr_string):
        if '/' not in cidr_string:
            raise SwaggerValidationError('CIDR {0} is invalid'.format(cidr_string))

    cidr_format = SwaggerFormat(
        # name of the format as used in the Swagger spec
        format='cidr',

        # Callable to convert a python CIDR object to a string
        to_wire=lambda cidr_object: cidr_object.cidr,

        # Callable to convert a string to a python CIDR object
        to_python=lambda cidr_string: CIDR(cidr_string),

        # Callable to validate the cidr in string form
        validate=validate_cidr
    )


Configuring user-defined formats
--------------------------------
Now that we have a ``cidr_format``, just pass it to a ``Spec`` as part of the
``config`` parameter on ``Spec`` creation.

.. code-block:: python

    from bravado_core.spec import Spec

    spec_dict = json.loads(open('swagger.json', 'r').read())
    config = {
        'validate_responses': True,
        'validate_requests': True,
        'formats': [cidr_format],
    }
    spec = Spec.from_dict(spec_dict, config=config)

All validation and processing of HTTP requests and responses will now use the
configured format where appropriate.


Putting it all together
-----------------------
A simple example of passing a CIDR object to a request and getting a list of
CIDR objects back from the response.

.. code-block:: json

    {
        "paths": {
            "/get_overlapping_cidrs": {
                "get": {
                    "parameters": [
                        {
                            "name": "cidr",
                            "in": "query",
                            "type": "string",
                            "format": "cidr"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "List of overlapping cidrs",
                            "schema": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "format": "cidr"
                                }
                            }
                        }
                    }
                }
            }
        }
    }

.. code-block:: python

    from bravado_core.spec import Spec
    from bravado_core.response import unmarshal_response
    from bravado_core.param import marshal_param

    # Retrieve the swagger spec from the server and json.load() it
    spec_dict = ...

    # Create cidr_format add it to the config dict
    config = ...

    # Create a bravado_core.spec.Spec
    swagger_spec = Spec.from_dict(spec_dict, config=config)

    # Get the operation to invoke
    op = swagger_spec.get_op_for_request('GET', '/get_overlapping_cidrs')

    # Get the Param that represents the cidr query parameter
    cidr_param = op.params.get('cidr')

    # Create a CIDR object - to_wire() will be called on this during marshalling
    cidr_object = CIDR('192.168.1.1/24)
    request_dict = {}

    # Marshal the cidr_object into the request_dict.
    marshal_param(cidr_param, cidr_object, request_dict)

    # Lots of hand-wavey stuff here - use whatever http client you have to
    # send the request and receive a response
    response = http_client.send(request_dict)

    # Extract the list of cidrs
    cidrs = unmarshal_response(response)

    # Verify cidrs are CIDR objects and not strings
    for cidr in cidrs:
        assert type(cidr) == CIDR
