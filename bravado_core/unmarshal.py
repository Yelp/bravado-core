# -*- coding: utf-8 -*-
import warnings

import typing
from six import iteritems

from bravado_core import _decorators
from bravado_core import schema
from bravado_core._compat import wraps
from bravado_core.exception import SwaggerMappingError
from bravado_core.model import MODEL_MARKER
from bravado_core.schema import collapsed_properties
from bravado_core.schema import get_type_from_schema
from bravado_core.schema import is_dict_like
from bravado_core.schema import is_list_like
from bravado_core.schema import SWAGGER_PRIMITIVES
from bravado_core.util import memoize_by_id


if getattr(typing, 'TYPE_CHECKING', False):
    from bravado_core.spec import Spec
    from bravado_core.model import Model
    from bravado_core._compat_typing import JSONDict
    from bravado_core._compat_typing import UnmarshalingMethod
    from bravado_core._compat_typing import NoReturn


_NOT_FOUND = object()


def unmarshal_schema_object(swagger_spec, schema_object_spec, value):
    # type: (Spec, JSONDict, typing.Any) -> typing.Any
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
    # type: (Spec, JSONDict, typing.Any) -> typing.Any
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
    # type: (Spec, JSONDict, typing.Any) -> typing.Any
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
    # type: (Spec, JSONDict, typing.Any) -> typing.Any
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
    # type: (Spec, JSONDict, typing.Any) -> typing.Any
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
    # type: (Spec, JSONDict, bool) -> UnmarshalingMethod
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
        @wraps(_unknown_type_unmarhsaling)
        def wrapper_unknown(value):
            # type: (typing.Any) -> typing.Any
            return _unknown_type_unmarhsaling(object_type, value)

        return wrapper_unknown


def _no_op_unmarshaling(value):
    # type: (typing.Any) -> typing.Any
    return value


def _unknown_type_unmarhsaling(object_type, value):
    # type: (typing.Union[typing.Type[dict], typing.Type[Model]], typing.Any) -> NoReturn
    raise SwaggerMappingError(
        "Don't know how to unmarshal value {0} with a type of {1}".format(
            value, object_type,
        ),
    )


def _raise_unknown_model(model_name, value):
    # type: (typing.Text, typing.Any) -> NoReturn
    raise SwaggerMappingError('Unknown model {0} when trying to unmarshal {1}'.format(model_name, value))


def _unmarshal_array(unmarshal_array_item_function, value):
    # type: (UnmarshalingMethod, typing.Any) -> typing.Any
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
    # type: (Spec, JSONDict) -> UnmarshalingMethod
    item_schema = swagger_spec.deref(swagger_spec.deref(object_schema).get('items', _NOT_FOUND))
    if item_schema is _NOT_FOUND:
        return _no_op_unmarshaling

    @wraps(_unmarshal_array)
    def wrapper_array(value):
        # type: (typing.Any) -> typing.Any
        return _unmarshal_array(
            get_unmarshaling_method(swagger_spec, item_schema),
            value,
        )

    return wrapper_array


def _unmarshaling_method_file(swagger_spec, object_schema):
    # type: (Spec, JSONDict) -> UnmarshalingMethod
    return _no_op_unmarshaling


def _unmarshal_object(
    properties_to_unmarshaling_function,  # type: typing.Dict[typing.Text, UnmarshalingMethod]
    discriminator_property,  # type: typing.Optional[typing.Text]
    model_to_unmarshaling_function_mapping,  # type: typing.Optional[typing.Dict[typing.Text, UnmarshalingMethod]]
    model_type,  # type: typing.Union[typing.Type[JSONDict], typing.Type[Model]]
    include_missing_properties,  # type: bool
    properties_to_default_value,  # type: JSONDict
    additional_properties_unmarshaling_function,  # type: UnmarshalingMethod
    model_value,  # type: typing.Any
):
    # type: (...) -> typing.Any
    """
    Unmarshal a dict into a Model instance or a dictionary (according to the 'use_models' swagger_spec configuration).

    :type model_type: Model
    :type model_value: dict

    :rtype: Model instance
    :raises: SwaggerMappingError
    """

    if not is_dict_like(model_value):
        raise SwaggerMappingError(
            "Expected type to be dict for value {0} to unmarshal to a {1}."
            "Was {2} instead.".format(model_value, model_type, type(model_value)),
        )

    if discriminator_property and model_to_unmarshaling_function_mapping:
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
    # type: (Spec, JSONDict, bool) -> UnmarshalingMethod
    # TODO: use_models parameter should be removed once unmarshal_model function is removed
    model_type = None  # type: typing.Optional[typing.Type[Model]]
    object_schema = swagger_spec.deref(object_schema)
    if MODEL_MARKER in object_schema:
        model_name = object_schema[MODEL_MARKER]
        model_type = swagger_spec.definitions.get(model_name)
        if use_models and model_type is None:
            @wraps(_raise_unknown_model)
            def wrapper_raise(value):
                # type: (typing.Any) -> typing.Any
                return _raise_unknown_model(model_name, value)

            return wrapper_raise
        if not use_models:
            model_type = None

    additional_properties_unmarshaling_function = _no_op_unmarshaling
    properties = collapsed_properties(object_schema, swagger_spec)
    required_properties = object_schema.get('required', [])
    if object_schema.get('additionalProperties') is not False:
        additional_properties_schema = object_schema.get('additionalProperties', {})
        if additional_properties_schema in ({}, True):
            additional_properties_unmarshaling_function = _no_op_unmarshaling
        else:
            additional_properties_unmarshaling_function = get_unmarshaling_method(
                swagger_spec, additional_properties_schema,
            )

    properties_to_unmarshaling_function = {
        prop_name: get_unmarshaling_method(
            swagger_spec,
            prop_schema,
            prop_schema.get('x-nullable', False) or prop_name not in required_properties,
        )
        for prop_name, prop_schema in iteritems(properties)
    }

    discriminator_property = object_schema.get('discriminator') if model_type is not None else None

    model_to_unmarshaling_function_mapping = None  # type: typing.Optional[typing.Dict[typing.Text, UnmarshalingMethod]]
    if model_type is not None and discriminator_property is not None:  # model type check kept to have mypy happy
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

    @wraps(_unmarshal_object)
    def wrapper_unmarsha(value):
        # type: (typing.Any) -> typing.Any
        return _unmarshal_object(
            properties_to_unmarshaling_function,
            discriminator_property,
            model_to_unmarshaling_function_mapping,
            model_type if model_type and swagger_spec.config['use_models'] else dict,
            swagger_spec.config['include_missing_properties'],
            properties_to_default_value,
            additional_properties_unmarshaling_function,
            value,
        )
    return wrapper_unmarsha


def _unmarshaling_method_primitive_type(swagger_spec, object_schema):
    # type: (Spec, JSONDict) -> UnmarshalingMethod
    swagger_format = schema.get_format(swagger_spec, object_schema)
    if swagger_format is not None:
        return swagger_spec.get_format(swagger_format).to_python
    else:
        return _no_op_unmarshaling
