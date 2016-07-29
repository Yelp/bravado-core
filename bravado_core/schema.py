from collections import Mapping

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
    return 'default' in swagger_spec.deref(schema_object_spec)


def get_default(swagger_spec, schema_object_spec):
    return swagger_spec.deref(schema_object_spec).get('default')


def is_required(swagger_spec, schema_object_spec):
    return swagger_spec.deref(schema_object_spec).get('required', False)


def has_format(swagger_spec, schema_object_spec):
    return 'format' in swagger_spec.deref(schema_object_spec)


def get_format(swagger_spec, schema_object_spec):
    return swagger_spec.deref(schema_object_spec).get('format')


def is_param_spec(swagger_spec, schema_object_spec):
    return 'in' in swagger_spec.deref(schema_object_spec)


def is_prop_nullable(swagger_spec, schema_object_spec):
    return swagger_spec.deref(schema_object_spec).get('x-nullable', False)


def is_ref(spec):
    return is_dict_like(spec) and '$ref' in spec


def is_dict_like(spec):
    """
    :param spec: swagger object specification in dict form
    :rtype: boolean
    """
    return isinstance(spec, Mapping)


def is_list_like(spec):
    """
    :param spec: swagger object specification in dict form
    :rtype: boolean
    """
    return type(spec) in (list, tuple)


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
    deref = swagger_spec.deref
    props_spec = deref(object_spec).get('properties', {})
    prop_spec = deref(props_spec).get(prop_name)

    if prop_spec is not None:
        return deref(prop_spec)

    additional_props = deref(object_spec).get('additionalProperties', True)

    if isinstance(additional_props, bool):
        # no spec for additional properties to conform to - this is basically
        # a way to send pretty much anything across the wire as is.
        return None

    additional_props = deref(additional_props)
    if is_dict_like(additional_props):
        # spec that all additional props MUST conform to
        return additional_props

    raise SwaggerMappingError(
        "Don't know what to do with `additionalProperties` in spec {0} "
        "when inspecting value {1}".format(object_spec, object_value))
