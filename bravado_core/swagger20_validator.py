import functools

from jsonschema import validators, _validators
from jsonschema.exceptions import ValidationError
from jsonschema.validators import Draft4Validator

from bravado_core.schema import is_param_spec
from bravado_core.schema import is_prop_nullable
from bravado_core.schema import is_required
from swagger_spec_validator.ref_validators import in_scope

"""Draft4Validator is not completely compatible with Swagger 2.0 schema
objects like parameter, etc. Swagger20Validator is an extension of
Draft4Validator which customizes/wraps some of the operations of the default
validator.
"""


def type_validator(swagger_spec, validator, types, instance, schema):
    """Skip the `type` validator when a Swagger parameter value is None.
    Otherwise it will fail with a "None is not a valid type" failure instead
    of letting the downstream `required_validator` do its job.
    Also skip when a Swagger property value is None and the schema contains
    the extension field `x-nullable` set to True.
    In all other cases, delegate to the existing Draft4 `type` validator.

    :param swagger_spec: needed for access to deref()
    :type swagger_spec: :class:`bravado_core.spec.Spec`
    :param validator: Validator class used to validate the object
    :type validator: :class:`Swagger20Validator` or
        :class:`jsonschema.validators.Draft4Validator`
    :param types: validate types
    :type types: string or list
    :param instance: object instance value
    :param schema: swagger spec for the object
    :type schema: dict
    """
    if (is_param_spec(swagger_spec, schema) or
            is_prop_nullable(swagger_spec, schema)) and instance is None:
        return

    for error in _validators.type_draft4(validator, types, instance, schema):
        yield error


def required_validator(swagger_spec, validator, required, instance, schema):
    """Swagger 2.0 expects `required` to be a bool in the Parameter object,
    but a list of properties everywhere else.

    :param swagger_spec: needed for access to deref()
    :type swagger_spec: :class:`bravado_core.spec.Spec`
    :param validator: Validator class used to validate the object
    :type validator: :class:`Swagger20Validator` or
        :class:`jsonschema.validators.Draft4Validator`
    :param required: value of `required` field
    :type required: boolean or list or None
    :param instance: object instance value
    :param schema: swagger spec for the object
    :type schema: dict
    """
    if is_param_spec(swagger_spec, schema):
        if required and instance is None:
            yield ValidationError('{0} is a required parameter.'.format(
                schema['name']))
    else:
        for error in _validators.required_draft4(validator, required, instance,
                                                 schema):
            yield error


def enum_validator(swagger_spec, validator, enums, instance, schema):
    """Swagger 2.0 allows enums to be validated against objects of type
    arrays, like query parameter (collectionFormat: multi)

    :param swagger_spec: needed for access to deref()
    :type swagger_spec: :class:`bravado_core.spec.Spec`
    :param validator: Validator class used to validate the object
    :type validator: :class: `Swagger20Validator` or
        :class: `jsonschema.validators.Draft4Validator`
    :param enums: allowed enum values
    :type enums: list
    :param instance: enum instance value
    :param schema: swagger spec for the object
    :type schema: dict
    """
    if schema.get('type') == 'array':
        for element in instance:
            for error in _validators.enum(validator, enums, element, schema):
                yield error
        return

    # Handle optional enum params with no value
    if is_param_spec(swagger_spec, schema):
        if not is_required(swagger_spec, schema) and instance is None:
            return

    for error in _validators.enum(validator, enums, instance, schema):
        yield error


def ref_validator(validator, ref, instance, schema):
    """When validating a request or response that contain $refs, jsonschema's
     RefResolver only contains scope (RefResolver._scopes_stack) for the
     request_spec or response_spec that it is fed. This scope doesn't contain
     the full scope built when ingesting the spec from its root
     (#/ in swagger.json). So, we need to modify the behavior of ref
     validation to use the `x-scope` annotations that were created during spec
     ingestion (see post_process_spec in spec.py).

    :param validator: Validator class used to validate the object
    :type validator: :class: `Swagger20Validator` or
        :class: `jsonschema.validators.Draft4Validator`
    :param ref: the target of the ref. eg. #/foo/bar/Baz
    :type ref: string
    :param instance: the object being validated
    :param schema: swagger spec that contains the ref.
        eg {'$ref': '#/foo/bar/Baz'}
    :type schema: dict
    """
    # This is a copy of jsonscehama._validators.ref(..) with the
    # in_scope(..) context manager applied before any refs are resolved.
    resolve = getattr(validator.resolver, "resolve")
    if resolve is None:
        with in_scope(validator.resolver, schema):
            with validator.resolver.resolving(ref) as resolved:
                for error in validator.descend(instance, resolved):
                    yield error
    else:
        with in_scope(validator.resolver, schema):
            scope, resolved = validator.resolver.resolve(ref)
        validator.resolver.push_scope(scope)

        try:
            for error in validator.descend(instance, resolved):
                yield error
        finally:
            validator.resolver.pop_scope()


def get_validator_type(swagger_spec):
    """Create a custom jsonschema validator for Swagger 2.0 specs.

    :rtype: Its complicated. See jsonschema.validators.create()
    """
    return validators.extend(
        Draft4Validator,
        {
            '$ref': ref_validator,
            'required': functools.partial(required_validator, swagger_spec),
            'enum': functools.partial(enum_validator, swagger_spec),
            'type': functools.partial(type_validator, swagger_spec),
        })
