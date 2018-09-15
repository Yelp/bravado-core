# -*- coding: utf-8 -*-
import pytest
from jsonschema.exceptions import ValidationError
from six import iteritems

from bravado_core.spec import Spec
from bravado_core.validate import validate_object
from tests.conftest import get_url
from tests.validate.conftest import email_address_format


@pytest.fixture
def address_spec():
    return {
        'type': 'object',
        'properties': {
            'number': {
                'type': 'number'
            },
            'street_name': {
                'type': 'string'
            },
            'street_type': {
                'type': 'string',
                'enum': [
                    'Street',
                    'Avenue',
                    'Boulevard',
                ]
            }
        }
    }


@pytest.fixture
def allOf_spec(address_spec):
    return {
        'allOf': [
            {
                'type': 'object',
                'properties': {
                    'business': {
                        'type': 'string'
                    },
                },
                'required': ['business'],
            },
            address_spec,
        ]
    }


def test_success(minimal_swagger_spec, address_spec):
    address = {
        'number': 1000,
        'street_name': 'Main',
        'street_type': 'Street',
    }
    validate_object(minimal_swagger_spec, address_spec, address)


def test_leaving_out_property_OK(minimal_swagger_spec, address_spec):
    address = {
        'street_name': 'Main',
        'street_type': 'Street',
    }
    validate_object(minimal_swagger_spec, address_spec, address)


def test_additional_property_OK(minimal_swagger_spec, address_spec):
    address = {
        'number': 1000,
        'street_name': 'Main',
        'street_type': 'Street',
        'city': 'Swaggerville'
    }
    validate_object(minimal_swagger_spec, address_spec, address)


def test_required_OK(minimal_swagger_spec, address_spec):
    address_spec['required'] = ['number']
    address = {
        'street_name': 'Main',
        'street_type': 'Street',
    }
    with pytest.raises(ValidationError) as excinfo:
        validate_object(minimal_swagger_spec, address_spec, address)
    assert 'is a required property' in str(excinfo.value)


def test_property_with_no_schema(minimal_swagger_spec, address_spec):
    address = {
        'number': 1000,
        'street_name': 'Main',
        'street_type': 'Street',
    }
    del address_spec['properties']['street_name']['type']
    validate_object(minimal_swagger_spec, address_spec, address)


@pytest.fixture
def email_address_object_spec():
    return {
        'type': 'object',
        'required': ['email_address'],
        'properties': {
            'email_address': {
                'type': 'string',
                'format': 'email_address',
            }
        }
    }


def test_user_defined_format_success(minimal_swagger_spec,
                                     email_address_object_spec):
    request_body = {'email_address': 'foo@bar.com'}
    minimal_swagger_spec.register_format(email_address_format)
    # No exception thrown == success
    validate_object(minimal_swagger_spec,
                    email_address_object_spec, request_body)


def test_user_defined_format_failure(minimal_swagger_spec,
                                     email_address_object_spec):
    request_body = {'email_address': 'i_am_not_a_valid_email_address'}
    minimal_swagger_spec.register_format(email_address_format)
    with pytest.raises(ValidationError) as excinfo:
        validate_object(minimal_swagger_spec, email_address_object_spec,
                        request_body)
    assert "'i_am_not_a_valid_email_address' is not a 'email_address'" in \
        str(excinfo.value)


def test_user_defined_format_sensitive_failure(
    minimal_swagger_spec, email_address_object_spec,
):
    object_properties = email_address_object_spec['properties']
    object_properties['email_address']['x-sensitive'] = True
    request_body = {'email_address': 'i_am_not_a_valid_email_address'}
    minimal_swagger_spec.register_format(email_address_format)
    with pytest.raises(ValidationError) as excinfo:
        validate_object(minimal_swagger_spec, email_address_object_spec,
                        request_body)
    assert "'i_am_not_a_valid_email_address'" not in str(excinfo.value)


def test_builtin_format_still_works_when_user_defined_format_used(
        minimal_swagger_spec):
    ipaddress_spec = {
        'type': 'object',
        'required': ['ipaddress'],
        'properties': {
            'ipaddress': {
                'type': 'string',
                'format': 'ipv4',
            }
        }
    }
    request_body = {'ipaddress': 'not_an_ip_address'}
    minimal_swagger_spec.register_format(email_address_format)
    with pytest.raises(ValidationError) as excinfo:
        validate_object(minimal_swagger_spec, ipaddress_spec, request_body)
    assert "'not_an_ip_address' is not a 'ipv4'" in str(excinfo.value)


def test_recursive_ref_depth_1(recursive_swagger_spec):
    validate_object(
        recursive_swagger_spec,
        {'$ref': '#/definitions/Node'},
        {'name': 'foo'})


def test_recursive_ref_depth_n(recursive_swagger_spec):
    value = {
        'name': 'foo',
        'child': {
            'name': 'bar',
            'child': {
                'name': 'baz'
            }
        }
    }
    validate_object(
        recursive_swagger_spec,
        {'$ref': '#/definitions/Node'},
        value)


def test_recursive_ref_depth_n_failure(recursive_swagger_spec):
    value = {
        'name': 'foo',
        'child': {
            'name': 'bar',
            'child': {
                'kaboom': 'baz'  # <-- key should be 'name', not 'kabbom'
            }
        }
    }
    with pytest.raises(ValidationError) as excinfo:
        validate_object(
            recursive_swagger_spec,
            {'$ref': '#/definitions/Node'},
            value)
    assert "'name' is a required property" in str(excinfo.value)


# x-nullable validation
# ---------------------
# If the value is an object, validation should pass if
# `x-nullable` is `True` and the value is `None`. `required` doesn't
# have an influence.
#
# +---------------------+-------------------------+--------------------------+
# |                     | required == False       | required == True         |
# +---------------------+-------------------------+--------------------------+
# | x-nullable == False | {}          -> pass (1) | {}          -> fail  (4) |
# |                     | {'x': 'y'}  -> pass (2) | {'x': 'y'}  -> pass  (5) |
# |                     | {'x': None} -> fail (3) | {'x': None} -> fail  (6) |
# +---------------------+-------------------------+--------------------------+
# | x-nullable == True  | {}          -> pass (7) | {}          -> fail (10) |
# |                     | {'x': 'y'}  -> pass (8) | {'x': 'y'}  -> pass (11) |
# |                     | {'x': None} -> pass (9) | {'x': None} -> pass (12) |
# +---------------------+-------------------------+--------------------------+


def content_spec_factory(required, nullable):
    return {
        'type': 'object',
        'required': ['x'] if required else [],
        'properties': {
            'x': {
                'type': 'string',
                'x-nullable': nullable,
            }
        }
    }


@pytest.mark.parametrize('nullable', [True, False])
@pytest.mark.parametrize('required', [True, False])
def test_nullable_with_value(empty_swagger_spec, nullable, required):
    """With a value set, validation should always pass: (2), (5), (8), (11)"""
    content_spec = content_spec_factory(required, nullable)
    value = {'x': 'y'}

    validate_object(empty_swagger_spec, content_spec, value)


@pytest.mark.parametrize('nullable', [True, False])
def test_nullable_required_no_value(empty_swagger_spec, nullable):
    """When the value is required but not set at all, validation
    should fail: (4), (10)
    """
    content_spec = content_spec_factory(True, nullable)
    value = {}

    with pytest.raises(ValidationError) as excinfo:
        validate_object(empty_swagger_spec, content_spec, value)
    assert "'x' is a required property" in str(excinfo.value.message)


@pytest.mark.parametrize('nullable', [True, False])
def test_nullable_no_value(empty_swagger_spec, nullable):
    """When the value is not required and not set at all, validation
    should pass: (1), (7)
    """
    content_spec = content_spec_factory(False, nullable=nullable)
    value = {}

    validate_object(empty_swagger_spec, content_spec, value)


@pytest.mark.parametrize('required', [True, False])
def test_nullable_false_value_none(empty_swagger_spec, required):
    """When nullable is `False` and the value is set to `None`, validation
    should fail: (3), (6)
    """
    content_spec = content_spec_factory(required, False)
    value = {'x': None}

    with pytest.raises(ValidationError) as excinfo:
        validate_object(empty_swagger_spec, content_spec, value)
    assert excinfo.value.message == "None is not of type 'string'"


@pytest.mark.parametrize('required', [True, False])
def test_nullable_none_value(empty_swagger_spec, required):
    """When nullable is `True` and the value is set to `None`, validation
    should pass: (9), (12)
    """
    content_spec = content_spec_factory(required, True)
    value = {'x': None}

    validate_object(empty_swagger_spec, content_spec, value)


def test_allOf_minimal(empty_swagger_spec, allOf_spec):
    value = {
        'business': 'Yelp',
    }

    validate_object(empty_swagger_spec, allOf_spec, value)


def test_allOf_fails(empty_swagger_spec, allOf_spec):
    with pytest.raises(ValidationError) as excinfo:
        validate_object(empty_swagger_spec, allOf_spec, {})
    assert excinfo.value.message == "'business' is a required property"


def test_allOf_complex(composition_spec):
    pongclone_spec = composition_spec.spec_dict['definitions']['pongClone']

    value = {
        'additionalFeature': 'Badges',
        'gameSystem': 'NES',
        'pang': 'value',
        'releaseDate': 'October',
    }

    validate_object(composition_spec, pongclone_spec, value)


def test_allOf_complex_failure(composition_spec):
    pongclone_spec = composition_spec.spec_dict['definitions']['pongClone']

    value = {
        'additionalFeature': 'Badges',
        'pang': 'value',
        'releaseDate': 'October',
    }

    with pytest.raises(ValidationError) as excinfo:
        validate_object(composition_spec, pongclone_spec, value)
    assert "'gameSystem' is a required property" in str(excinfo.value.message)


def test_validate_valid_polymorphic_object(polymorphic_spec):
    list_of_pets_dict = {
        'number_of_pets': 3,
        'list': [
            {
                'name': 'a generic pet name',
                'type': 'GenericPet',
            },
            {
                'name': 'a dog name',
                'type': 'Dog',
                'birth_date': '2017-03-09',
            },
            {
                'name': 'a cat name',
                'type': 'Cat',
                'color': 'white',
            },
        ]
    }
    validate_object(
        swagger_spec=polymorphic_spec,
        object_spec=polymorphic_spec.spec_dict['definitions']['PetList'],
        value=list_of_pets_dict,
    )


@pytest.mark.parametrize(
    'schema_dict, expected_validation_error',
    (
        [
            {
                'number_of_pets': 1,
                'list': [
                    {
                        'name': 'a cat name',
                        'type': 'Dog',
                        'color': 'white',
                    },
                ]
            },
            '\'birth_date\' is a required property',
        ],
        [
            {
                'number_of_pets': 1,
                'list': [
                    {
                        'name': 'any string',
                        'type': 'a not defined type',
                    },
                ]
            },
            '\'a not defined type\' is not a recognized schema',
        ],
        [
            {
                'number_of_pets': 1,
                'list': [
                    {
                        'name': 'a bird name',
                        'type': 'Bird',
                    },
                ]
            },
            'discriminated schema \'Bird\' must inherit from \'GenericPet\'',
        ],
        [
            {
                'number_of_pets': 1,
                'list': [
                    {
                        'name': 'a whale name',
                        'type': 'Whale',
                        'weight': 1000,
                    },
                ]
            },
            'discriminated schema \'Whale\' must inherit from \'GenericPet\'',
        ],
    )
)
def test_validate_invalid_polymorphic_object(polymorphic_spec, schema_dict, expected_validation_error):
    with pytest.raises(ValidationError) as e:
        validate_object(
            swagger_spec=polymorphic_spec,
            object_spec=polymorphic_spec.spec_dict['definitions']['PetList'],
            value=schema_dict,
        )
    assert expected_validation_error in str(e.value.message)


def test_validate_invalid_polymorphic_does_not_alter_validation_paths(polymorphic_spec):
    dog_dict = {
        'name': 'This is a dog name',
        'type': 'Dog',
        # 'birth_date' this is intentionally removed in order to trigger a validation error
    }

    with pytest.raises(ValidationError) as excinfo:
        validate_object(
            swagger_spec=polymorphic_spec,
            object_spec=polymorphic_spec.definitions['GenericPet']._model_spec,
            value=dog_dict,
        )

    validation_error = excinfo.value
    assert validation_error.validator == 'required'
    assert validation_error.validator_value == ['birth_date']
    assert validation_error.message == '\'birth_date\' is a required property'
    # as birth_date is defined on the 2nd item of the Dog allOf list the expected schema path should be allOf/1/required
    assert list(validation_error.schema_path) == ['allOf', 1, 'required']


@pytest.mark.parametrize('internally_dereference_refs', [True, False])
def test_validate_object_with_recursive_definition(
    polymorphic_abspath, polymorphic_dict, internally_dereference_refs,
):
    # The goal of this test is to ensure that recursive definitions are properly handled
    # even if internally_dereference_refs is enabled.
    # Introduce a recursion definition into vendor extensions, this "trick" could be used
    # to force bravado-core to recognize models that are defined on #/definitions of
    # referenced files or defined on un-referenced files
    polymorphic_dict['definitions']['GenericPet']['x-referred-schema'] = [
        {'$ref': '#/definitions/{}'.format(definition_key)}
        for definition_key, definition in iteritems(polymorphic_dict['definitions'])
        if {'$ref': '#/definitions/GenericPet'} in definition.get('allOf', [])
    ]

    polymorphic_spec = Spec.from_dict(
        spec_dict=polymorphic_dict,
        origin_url=get_url(polymorphic_abspath),
        config={'internally_dereference_refs': internally_dereference_refs},
    )

    dog_dict = {
        'name': 'This is a dog name',
        'type': 'Dog',
        'birth_date': '2018-01-01',
    }

    try:
        validate_object(
            swagger_spec=polymorphic_spec,
            object_spec=polymorphic_spec.definitions['GenericPet']._model_spec,
            value=dog_dict,
        )
    except RuntimeError:  # Not catching RecursionError as it was introduced in Python 3.5+
        pytest.fail('Unbounded recursion has been detected while calling validate_object')
