from jsonschema import validators, _validators
from jsonschema.exceptions import ValidationError
from jsonschema.validators import Draft4Validator

from bravado_core.schema import is_param_spec

"""Draft4Validator is not completely compatible with Swagger 2.0 schema
objects like parameter, etc. Swagger20Validator is an extension of
Draft4Validator which customizes/wraps some of the operations of the default
validator.
"""


def ignore(_validator, *args):
    """A validator which performs no validation. Used to `ignore` some schema
    fields during validation.
    """
    return


def type_validator(validator, types, instance, schema):
    """Skip the `type` validator when a Swagger parameter value is None.
    Otherwise it will fail with a "None is not a valid type" failure instead
    of letting the downstream `required_validator` do its job. In all other
    cases, delegate to the existing Draft4 `type` validator.

    :param validator: Validator class used to validate the object
    :type validator: :class:`Swagger20Validator` or
        :class:`jsonschema.validators.Draft4Validator`
    :param types: validate types
    :type types: string or list
    :param instance: object instance value
    :param schema: swagger spec for the object
    :type schema: dict
    """
    if is_param_spec(schema) and instance is None:
        return

    return _validators.type_draft4(validator, types, instance, schema)


def required_validator(validator, required, instance, schema):
    """Swagger 2.0 expects `required` to be a bool in the Parameter object,
    but a list of properties everywhere else.

    :param validator: Validator class used to validate the object
    :type validator: :class:`Swagger20Validator` or
        :class:`jsonschema.validators.Draft4Validator`
    :param required: value of `required` field
    :type required: boolean or list or None
    :param instance: object instance value
    :param schema: swagger spec for the object
    :type schema: dict
    """
    if is_param_spec(schema):
        if required and instance is None:
            return [ValidationError("%s is required" % schema['name'])]
    else:
        return _validators.required_draft4(
            validator, required, instance, schema)


def enum_validator(validator, enums, instance, schema):
    """Swagger 2.0 allows enums to be validated against objects of type
    arrays, like query parameter (collectionFormat: multi)

    :param validator: Validator class used to validate the object
    :type validator: :class: `Swagger20Validator` or
                             `jsonschema.validators.Draft4Validator`
    :param enums: allowed enum values
    :type enums: list
    :param instance: enum instance value
    :param schema: swagger spec for the object
    :type schema: dict
    """
    if schema.get('type') == 'array':
        return (v for item in instance for v in _validators.enum(
            validator, enums, item, schema))
    return _validators.enum(validator, enums, instance, schema)


Swagger20Validator = validators.extend(
    Draft4Validator,
    {
        'required': required_validator,
        'enum': enum_validator,
        'type': type_validator,
    })
