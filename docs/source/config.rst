Configuration
=============

All configuration is stored in a ``dict``.

.. code-block:: python

    from bravado_core.spec import Spec

    spec_dict = json.loads(open('swagger.json', 'r').read())

    config = {
        'validate_requests': False,
        'use_models': False,
    }

    swagger_spec = Spec.from_dict(spec_dict, config=config)



============================= =============== ========= ====================================================
Config key                    Type            Default   Description
----------------------------- --------------- --------- ----------------------------------------------------
*validate_swagger_spec*       boolean         True      | Validate the Swagger spec against
                                                        | the Swagger 2.0 Specification.
----------------------------- --------------- --------- ----------------------------------------------------
*validate_requests*           boolean         True      | On the client side, validates outgoing requests.
                                                        | On the server side, validates incoming requests.
----------------------------- --------------- --------- ----------------------------------------------------
*validate_responses*          boolean         True      | On the client side, validates incoming responses.
                                                        | On the server side, validates outgoing responses.
----------------------------- --------------- --------- ----------------------------------------------------
*use_models*                  boolean         True      | Use python classes to represent models
                                                        | instead of dicts. See :ref:`models`.
----------------------------- --------------- --------- ----------------------------------------------------
*formats*                     list of         []        | List of user-defined formats to support.
                              SwaggerFormat             | See :ref:`formats`.
----------------------------- --------------- --------- ----------------------------------------------------
*include_missing_properties*   boolean         True     | Create properties with the value ``None`` if they
                                                        | were not submitted during object unmarshalling
----------------------------- --------------- --------- ----------------------------------------------------
*default_type_to_object*      boolean         False     | When set to ``True``, missing types will default
                                                        | to ``object`` and be validated as such.
                                                        | When set to ``False``, missing types will not be
                                                        | validated at all.
----------------------------- --------------- --------- ----------------------------------------------------
*return_raw_response*         boolean         False     | When set to ``True``, the raw decoded response
                                                        | will be returned.
                                                        | When set to ``False``, the response will be
                                                        | unmarshalled according to the schema.
============================= =============== ========= ====================================================
