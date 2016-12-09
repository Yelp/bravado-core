"""
Delegate as much validation as possible out to jsonschema. This module serves
as the single point of entry for validations should we need to further
customize the behavior.
"""

from bravado_core.exception import SwaggerMappingError, SwaggerSecurityValidationError
from bravado_core.schema import SWAGGER_PRIMITIVES
from bravado_core.swagger20_validator import get_validator_type
from six import itervalues


def validate_schema_object(swagger_spec, schema_object_spec, value):
    """
    :raises ValidationError: when jsonschema validation fails.
    :raises SwaggerMappingError: on invalid Swagger `type`.
    :raises SwaggerValidationError: when user-defined format validation fails.
    """
    deref = swagger_spec.deref

    schemas = []

    all_of = deref(schema_object_spec.get('allOf'))
    if all_of is not None:
        schemas = [deref(sub_schema) for sub_schema in all_of]
    else:
        schemas = [deref(schema_object_spec)]

    for one_schema in schemas:
        obj_type = deref(one_schema.get('type'))

        if obj_type in SWAGGER_PRIMITIVES:
            validate_primitive(swagger_spec, one_schema, value)

        elif obj_type == 'array':
            validate_array(swagger_spec, one_schema, value)

        elif obj_type == 'object':
            validate_object(swagger_spec, one_schema, value)

        elif obj_type == 'file':
            pass

        else:
            raise SwaggerMappingError('Unknown type {0} for value {1}'.format(
                obj_type, value))


def validate_primitive(swagger_spec, primitive_spec, value):
    """
    :type swagger_spec: :class:`bravado_core.spec.Spec`
    :param primitive_spec: spec for a swagger primitive type in dict form
    :type value: int, string, float, long, etc
    """
    get_validator_type(swagger_spec)(
        primitive_spec,
        format_checker=swagger_spec.format_checker,
        resolver=swagger_spec.resolver).validate(value)


def validate_array(swagger_spec, array_spec, value):
    """
    :type swagger_spec: :class:`bravado_core.spec.Spec`
    :param spec: spec for an 'array' type in dict form
    :type value: list
    """
    get_validator_type(swagger_spec)(
        array_spec,
        format_checker=swagger_spec.format_checker,
        resolver=swagger_spec.resolver).validate(value)


def validate_object(swagger_spec, object_spec, value):
    """
    :type swagger_spec: :class:`bravado_core.spec.Spec`
    :param object_spec: spec for an 'object' type in dict form
    :type value: dict
    """
    get_validator_type(swagger_spec)(
        object_spec,
        format_checker=swagger_spec.format_checker,
        resolver=swagger_spec.resolver).validate(value)


def validate_security_object(op, request_data):
    """
    Checks that one security option is used at time.

    :param op: operation to be considered
    :type op: :class:`bravado_core.operation.Operation`
    :param request_data:
    :type request_data: dict
    :raise: SwaggerSecurityValidationError
    """

    security_types = set(
        definition.type
        for security_requirement in op.security_requirements
        for definition in itervalues(security_requirement.security_definitions)
    )

    # At the moment we are handling only apiKey securities
    if 'apiKey' in security_types:
        matched_security_indexes = []
        for security_index, security_params_list in enumerate(op.security_requirements):
            if all([request_data.get(security_param.name) is not None for security_param in security_params_list]):
                matched_security_indexes.append(security_index)

        if len(matched_security_indexes) == 0:
            raise SwaggerSecurityValidationError('No security definition used.')

        if len(matched_security_indexes) > 1:
            # if more than one security defs are matched then check if one security definition contains all the others
            # ie. consider sec1: requires parameter sec1 and sec2: requires parameter sec2
            # if an operation defines two securities like [{"sec1": []}, {"sec1": [], "sec2": []}]
            # it is acceptable to have:
            #   sec1 parameter only (match the first security)
            #   sec1 and sec2 (match the second security)

            # extract all the security matched security definition and sort them for decreasing length
            matched_security_definitions = sorted(
                (
                    set(security)
                    for index, security in enumerate(op.acceptable_security_definition_combinations)
                    if index in matched_security_indexes
                ), key=len, reverse=True
            )

            # have all the security definition the same length?
            # if yes is not possible to discriminate the security definition matched
            all_same_length = (len(matched_security_definitions[0]) == len(matched_security_definitions[-1]))

            # is the longest security definition a superset for all the others?
            # if no there is no way to discriminate the security definition matched
            exists_superset = all(
                matched_security_definitions[0].issuperset(security_definition)
                for security_definition in matched_security_definitions
            )

            if all_same_length or not exists_superset:
                raise SwaggerSecurityValidationError(
                    "More than one security definition is in use at the same time ({0})".format(
                        ', '.join(
                            str(security)
                            for index, security in enumerate(op.acceptable_security_definition_combinations)
                            if index in matched_security_indexes
                        )
                    )
                )
