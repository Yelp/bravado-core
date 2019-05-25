# -*- coding: utf-8 -*-
import warnings
from functools import partial

from six import iteritems

from bravado_core import _decorators
from bravado_core import schema
from bravado_core.exception import SwaggerMappingError
from bravado_core.model import MODEL_MARKER
from bravado_core.schema import collapsed_properties
from bravado_core.schema import get_type_from_schema
from bravado_core.schema import is_dict_like
from bravado_core.schema import is_list_like
from bravado_core.schema import SWAGGER_PRIMITIVES
from bravado_core.util import memoize_by_id


_NOT_FOUND = object()


def unmarshal_schema_object(swagger_spec, schema_object_spec, value):
    """
    Unmarshal the value using the given schema object specification.

    Unmarshalling includes:
    - transform the value according to 'format' if available
    - return the value in a form suitable for use. e.g. conversion to a Model
      type.

    :type swagger_spec: :class:`bravado_core.spec.Spec`
    :type schema_object_spec: dict
    :type value: int, float, long, string, unicode, boolean, list, dict, etc

    :return: unmarshalled value
    :rtype: int, float, long, string, unicode, boolean, list, dict, object (in
        the case of a 'format' conversion', or Model type
    """
    unmarshaling_method = get_unmarshaling_method(swagger_spec, schema_object_spec)
    return unmarshaling_method(value)


def unmarshal_primitive(swagger_spec, primitive_spec, value):
    """Unmarshal a jsonschema primitive type into a python primitive.

    :type swagger_spec: :class:`bravado_core.spec.Spec`
    :type primitive_spec: dict
    :type value: int, long, float, boolean, string, unicode, etc

    :rtype: int, long, float, boolean, string, unicode, or an object
        based on 'format'
    :raises: SwaggerMappingError
    """
    warnings.warn(
        'unmarshal_primitive will be deprecated in the next major release. '
        'Please use the more general entry-point offered in unmarshal_schema_object',
        DeprecationWarning,
    )
    null_decorator = _decorators.handle_null_value(swagger_spec, primitive_spec)
    unmarshal_function = _unmarshaling_method_primitive_type(swagger_spec, primitive_spec)
    return null_decorator(unmarshal_function)(value)


def unmarshal_array(swagger_spec, array_spec, array_value):
    """Unmarshal a jsonschema type of 'array' into a python list.

    :type swagger_spec: :class:`bravado_core.spec.Spec`
    :type array_spec: dict
    :type array_value: list
    :rtype: list
    :raises: SwaggerMappingError
    """
    warnings.warn(
        'unmarshal_array will be deprecated in the next major release. '
        'Please use the more general entry-point offered in unmarshal_schema_object',
        DeprecationWarning,
    )
    null_decorator = _decorators.handle_null_value(swagger_spec, array_spec)
    unmarshal_function = _unmarshaling_method_array(swagger_spec, array_spec)
    return null_decorator(unmarshal_function)(array_value)


def unmarshal_object(swagger_spec, object_spec, object_value):
    """Unmarshal a jsonschema type of 'object' into a python dict.

    :type swagger_spec: :class:`bravado_core.spec.Spec`
    :type object_spec: dict
    :type object_value: dict
    :rtype: dict
    :raises: SwaggerMappingError
    """
    warnings.warn(
        'unmarshal_object will be deprecated in the next major release. '
        'Please use the more general entry-point offered in unmarshal_schema_object',
        DeprecationWarning,
    )
    null_decorator = _decorators.handle_null_value(swagger_spec, object_spec)
    unmarshal_function = _unmarshaling_method_object(swagger_spec, object_spec, use_models=False)
    return null_decorator(unmarshal_function)(object_value)


def unmarshal_model(swagger_spec, model_spec, model_value):
    """Unmarshal a dict into a Model instance.

    :type swagger_spec: :class:`bravado_core.spec.Spec`
    :type model_spec: dict
    :type model_value: dict
    :rtype: Model instance
    :raises: SwaggerMappingError
    """
    warnings.warn(
        'unmarshal_model will be deprecated in the next major release. '
        'Please use the more general entry-point offered in unmarshal_schema_object',
        DeprecationWarning,
    )

    null_decorator = _decorators.handle_null_value(swagger_spec, model_spec)
    unmarshal_function = _unmarshaling_method_object(swagger_spec, model_spec, use_models=True)
    return null_decorator(unmarshal_function)(model_value)


@_decorators.wrap_recursive_call_exception
@memoize_by_id
def get_unmarshaling_method(swagger_spec, object_schema, is_nullable=True):
    # TODO: remove is_nullable support once https://github.com/Yelp/bravado-core/issues/335 is addressed
    """
    Determine the method needed to unmarshal values of a defined object_schema
    The returned method will accept a single positional parameter that represent the value
    to be unmarshaled.

    :type swagger_spec: :class:`bravado_core.spec.Spec`
    :type object_schema: dict
    """
    object_schema = swagger_spec.deref(object_schema)
    null_decorator = _decorators.handle_null_value(swagger_spec, object_schema, is_nullable)
    object_type = get_type_from_schema(swagger_spec, object_schema)

    if object_type == 'array':
        return null_decorator(_unmarshaling_method_array(swagger_spec, object_schema))
    elif object_type == 'file':
        # TODO: Type file is not a valid type. It is present to support parameter unmarshaling (move to bravado_core.param)  # noqa: E501
        return null_decorator(_unmarshaling_method_file(swagger_spec, object_schema))
    elif object_type == 'object':
        return null_decorator(_unmarshaling_method_object(swagger_spec, object_schema))
    elif object_type in SWAGGER_PRIMITIVES:
        return null_decorator(_unmarshaling_method_primitive_type(swagger_spec, object_schema))
    elif object_type is None:
        return _no_op_unmarshaling
    else:
        return partial(_unknown_type_unmarhsaling, object_type)


def _no_op_unmarshaling(value):
    return value


def _unknown_type_unmarhsaling(object_type, value):
    raise SwaggerMappingError(
        "Don't know how to unmarshal value {0} with a type of {1}".format(
            value, object_type,
        ),
    )


def _raise_unknown_model(model_name, value):
    raise SwaggerMappingError('Unknown model {0} when trying to unmarshal {1}'.format(model_name, value))


def _unmarshal_array(unmarshal_array_item_function, value):
    """
    Unmarshal a jsonschema type of 'array' into a python list.

    :type unmarshal_array_item_function: callable
    :type value: list
    :rtype: list
    :raises: SwaggerMappingError
    """
    if not is_list_like(value):
        raise SwaggerMappingError('Expected list like type for {0}:{1}'.format(type(value), value))

    return [
        unmarshal_array_item_function(item)
        for item in value
    ]


def _unmarshaling_method_array(swagger_spec, object_schema):
    item_schema = swagger_spec.deref(swagger_spec.deref(object_schema).get('items', _NOT_FOUND))
    if item_schema is _NOT_FOUND:
        return _no_op_unmarshaling

    return partial(
        _unmarshal_array,
        get_unmarshaling_method(swagger_spec, item_schema),
    )


def _unmarshaling_method_file(swagger_spec, object_schema):
    return _no_op_unmarshaling


def _unmarshal_object(
    properties_to_unmarshaling_function,
    discriminator_property,
    model_to_unmarshaling_function_mapping,
    model_type,
    include_missing_properties,
    properties_to_default_value,
    additional_properties_unmarshaling_function,
    model_value,
):
    """
    Unmarshal a dict into a Model instance or a dictionary (according to the 'use_models' swagger_spec configuration).

    :type model_type: Model
    :type model_value: dict

    :rtype: Model instance
    :raises: SwaggerMappingError
    """
    if model_type is None:
        model_type = dict

    if not is_dict_like(model_value):
        raise SwaggerMappingError(
            "Expected type to be dict for value {0} to unmarshal to a {1}."
            "Was {2} instead.".format(model_value, model_type, type(model_value)),
        )

    if discriminator_property:
        discriminated_model_unsmarhaling_function = model_to_unmarshaling_function_mapping.get(
            model_value[discriminator_property],
        )
        if discriminated_model_unsmarhaling_function:
            return discriminated_model_unsmarhaling_function(model_value)

    unmarshaled_value = model_type()
    for property_name, property_value in iteritems(model_value):
        unmarshaling_function = properties_to_unmarshaling_function.get(
            property_name, additional_properties_unmarshaling_function,
        )
        unmarshaled_value[property_name] = unmarshaling_function(property_value)

    if include_missing_properties:
        for property_name, unmarshaling_function in iteritems(properties_to_unmarshaling_function):
            if property_name not in unmarshaled_value:
                unmarshaled_value[property_name] = properties_to_default_value.get(property_name)

    return unmarshaled_value


def _unmarshaling_method_object(swagger_spec, object_schema, use_models=True):
    # TODO: use_models parameter should be removed once unmarshal_model function is removed
    model_type = None
    object_schema = swagger_spec.deref(object_schema)
    if MODEL_MARKER in object_schema:
        model_name = object_schema[MODEL_MARKER]
        model_type = swagger_spec.definitions.get(model_name)
        if use_models and model_type is None:
            return partial(_raise_unknown_model, model_name)
        if not use_models:
            model_type = None

    additional_properties_unmarshaling_function = _no_op_unmarshaling
    if model_type is None:
        properties = collapsed_properties(object_schema, swagger_spec)
        required_properties = object_schema.get('required', [])
        if not object_schema.get('additionalProperties') is False:
            additional_properties_schema = object_schema.get('additionalProperties', {})
            if additional_properties_schema in ({}, True):
                additional_properties_unmarshaling_function = _no_op_unmarshaling
            else:
                additional_properties_unmarshaling_function = get_unmarshaling_method(
                    swagger_spec, additional_properties_schema,
                )
    else:
        properties = model_type._properties
        required_properties = model_type._required_properties
        if not model_type._deny_additional_properties:
            additional_properties_unmarshaling_function = get_unmarshaling_method(
                swagger_spec, model_type._additional_properties_schema,
            )

    properties_to_unmarshaling_function = {}
    for prop_name, prop_schema in iteritems(properties):
        properties_to_unmarshaling_function[prop_name] = get_unmarshaling_method(
            swagger_spec,
            prop_schema,
            prop_schema.get('x-nullable', False) or prop_name not in required_properties,
        )

    discriminator_property = object_schema.get('discriminator') if model_type is not None else None

    model_to_unmarshaling_function_mapping = None
    if discriminator_property is not None:
        model_to_unmarshaling_function_mapping = {
            k: get_unmarshaling_method(
                swagger_spec,
                v._model_spec,
            )
            for k, v in iteritems(swagger_spec.definitions)
            if model_type.__name__ in v._inherits_from
        }

    properties_to_default_value = {
        prop_name: schema.get_default(swagger_spec, prop_schema)
        for prop_name, prop_schema in iteritems(properties)
        if schema.has_default(swagger_spec, prop_schema)
    }

    return partial(
        _unmarshal_object,
        properties_to_unmarshaling_function,
        discriminator_property,
        model_to_unmarshaling_function_mapping,
        model_type if model_type and model_type._use_models else None,
        model_type._include_missing_properties if model_type else swagger_spec.config['include_missing_properties'],
        properties_to_default_value,
        additional_properties_unmarshaling_function,
    )


def _unmarshaling_method_primitive_type(swagger_spec, object_schema):
    swagger_format = schema.get_format(swagger_spec, object_schema)
    if swagger_format is not None:
        return swagger_spec.get_format(swagger_format).to_python
    else:
        return _no_op_unmarshaling
