import jsonref

from bravado_core.exception import SwaggerMappingError

# 'object' and 'array' are omitted since this should really be read as
# "Swagger types that map to python primitives"
SWAGGER_PRIMITIVES = (
    'integer',
    'number',
    'string',
    'boolean',
    'null',
)


def has_default(swagger_spec, schema_object_spec):
    return swagger_spec.resolve(schema_object_spec, 'default') is not None


def get_default(swagger_spec, schema_object_spec):
    return swagger_spec.resolve(schema_object_spec, 'default')


def is_required(swagger_spec, schema_object_spec):
    return swagger_spec.resolve(schema_object_spec, 'required', False)


def has_format(swagger_spec, schema_object_spec):
    return swagger_spec.resolve(schema_object_spec, 'format') is not None


def get_format(swagger_spec, schema_object_spec):
    return swagger_spec.resolve(schema_object_spec, 'format')


def is_param_spec(swagger_spec, schema_object_spec):
    return swagger_spec.resolve(schema_object_spec, 'in') is not None


def is_dict_like(spec):
    """Since we're using jsonref, identifying dicts while inspecting a swagger
    spec is no longer limited to the dict type. This takes into account
    jsonref's proxy objects that dereference to a dict.

    :param spec: swagger object specification in dict form
    :rtype: boolean
    """
    if type(spec) == dict:
        return True
    # TODO: Remove when dependency on jsonref removed
    if type(spec) == jsonref.JsonRef and type(spec.__subject__) == dict:
        return True
    return False


def is_list_like(spec):
    """Since we're using jsonref, identifying arrays while inspecting a swagger
    spec is no longer limited to the list type. This takes into account
    jsonref's proxy objects that dereference to a list.

    :param spec: swagger object specification in dict form
    :rtype: boolean
    """
    if type(spec) == list:
        return True
    # TODO: Remove when dependency on jsonref removed
    if type(spec) == jsonref.JsonRef and type(spec.__subject__) == list:
        return True
    return False


def get_spec_for_prop(swagger_spec, object_spec, object_value, prop_name):
    """Given a jsonschema object spec and value, retrieve the spec for the
     given property taking 'additionalProperties' into consideration.

    :param object_spec: spec for a jsonschema 'object' in dict form
    :param object_value: jsonschema object containing the given property. Only
        used in error message.
    :param prop_name: name of the property to retrieve the spec for

    :return: spec for the given property or None if no spec found
    :rtype: dict
    """
    props_spec = swagger_spec.resolve(object_spec, 'properties', {})
    prop_spec = swagger_spec.resolve(props_spec, prop_name)

    if prop_spec is not None:
        return prop_spec

    additional_props = swagger_spec.resolve(
        object_spec, 'additionalProperties', True)

    if isinstance(additional_props, bool):
        # no spec for additional properties to conform to - this is basically
        # a way to send pretty much anything across the wire as is.
        return None

    if is_dict_like(additional_props):
        # spec that all additional props MUST conform to
        return additional_props

    raise SwaggerMappingError(
        "Don't know what to do with `additionalProperties` in spec {0} "
        "when inspecting value {1}".format(object_spec, object_value))
