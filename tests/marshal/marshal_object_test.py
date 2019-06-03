# -*- coding: utf-8 -*-
import datetime

import pytest
from dateutil.tz import tzutc

from bravado_core.exception import SwaggerMappingError
from bravado_core.marshal import marshal_object
from bravado_core.spec import Spec


@pytest.fixture
def address_spec():
    return {
        'type': 'object',
        'properties': {
            'number': {
                'type': 'number',
            },
            'street_name': {
                'type': 'string',
            },
            'street_type': {
                'type': 'string',
                'enum': [
                    'Street',
                    'Avenue',
                    'Boulevard',
                ],
            },
        },
    }


@pytest.fixture
def address():
    return {
        'number': 1600,
        'street_name': u'Ümlaut',
        'street_type': 'Avenue',
    }


def test_properties(empty_swagger_spec, address_spec, address):
    result = marshal_object(empty_swagger_spec, address_spec, address)
    assert address == result


def test_array(empty_swagger_spec, address_spec):
    tags_spec = {
        'type': 'array',
        'items': {
            'type': 'string',
        },
    }
    address_spec['properties']['tags'] = tags_spec
    address = {
        'number': 1600,
        'street_name': 'Pennsylvania',
        'street_type': 'Avenue',
        'tags': [
            'home',
            'best place on earth',
            'cul de sac',
        ],
    }
    result = marshal_object(empty_swagger_spec, address_spec, address)
    assert result == address


def test_nested_object(empty_swagger_spec, address_spec):
    location_spec = {
        'type': 'object',
        'properties': {
            'longitude': {
                'type': 'number',
            },
            'latitude': {
                'type': 'number',
            },
        },
    }
    address_spec['properties']['location'] = location_spec
    address = {
        'number': 1600,
        'street_name': 'Pennsylvania',
        'street_type': 'Avenue',
        'location': {
            'longitude': 100.1,
            'latitude': 99.9,
        },
    }
    result = marshal_object(empty_swagger_spec, address_spec, address)
    assert result == address


def test_model(minimal_swagger_dict, address_spec):
    location_spec = {
        'type': 'object',
        'properties': {
            'longitude': {
                'type': 'number',
            },
            'latitude': {
                'type': 'number',
            },
        },
    }
    minimal_swagger_dict['definitions']['Location'] = location_spec

    # The Location model type won't be built on schema ingestion unless
    # something actually references it. Create a throwaway response for this
    # purpose.
    location_response = {
        'get': {
            'responses': {
                '200': {
                    'description': 'A location',
                    'schema': {
                        '$ref': '#/definitions/Location',
                    },
                },
            },
        },
    }
    minimal_swagger_dict['paths']['/foo'] = location_response

    swagger_spec = Spec.from_dict(minimal_swagger_dict)
    address_spec['properties']['location'] = \
        swagger_spec.spec_dict['definitions']['Location']
    Location = swagger_spec.definitions['Location']
    address = {
        'number': 1600,
        'street_name': 'Pennsylvania',
        'street_type': 'Avenue',
        'location': Location(longitude=100.1, latitude=99.9),
    }

    expected_address = {
        'number': 1600,
        'street_name': 'Pennsylvania',
        'street_type': 'Avenue',
        'location': {
            'longitude': 100.1,
            'latitude': 99.9,
        },
    }

    result = marshal_object(swagger_spec, address_spec, address)
    assert expected_address == result


def test_object_not_dict_like_raises_error(
    empty_swagger_spec, address_spec,
):
    i_am_not_dict_like = 34
    with pytest.raises(SwaggerMappingError) as excinfo:
        marshal_object(empty_swagger_spec, address_spec, i_am_not_dict_like)

    assert "Expected type to be dict or Model to marshal value '{}' to a dict. Was {} instead.".format(
        i_am_not_dict_like, type(i_am_not_dict_like),
    ) in str(excinfo.value)


def test_missing_properties_not_marshaled(
    empty_swagger_spec, address_spec, address,
):
    del address['number']
    expected_address = {
        'street_name': u'Ümlaut',
        'street_type': 'Avenue',
    }
    result = marshal_object(empty_swagger_spec, address_spec, address)
    assert expected_address == result


def test_property_set_to_None_not_marshaled(
    empty_swagger_spec, address_spec, address,
):
    address['number'] = None
    expected_address = {
        'street_name': u'Ümlaut',
        'street_type': 'Avenue',
    }
    result = marshal_object(empty_swagger_spec, address_spec, address)
    assert expected_address == result


def test_pass_through_additionalProperties_with_no_spec(
    empty_swagger_spec, address_spec, address,
):
    address_spec['additionalProperties'] = True
    address['city'] = 'Swaggerville'
    expected_address = {
        'number': 1600,
        'street_name': u'Ümlaut',
        'street_type': 'Avenue',
        'city': 'Swaggerville',
    }
    result = marshal_object(empty_swagger_spec, address_spec, address)
    assert expected_address == result


def test_pass_through_property_with_no_spec(
    empty_swagger_spec, address_spec, address,
):
    del address_spec['properties']['street_name']['type']
    # add a field with a None value and no spec
    address['none_field'] = None
    result = marshal_object(empty_swagger_spec, address_spec, address)
    assert address == result


def test_ref(minimal_swagger_dict, address_spec, address):
    minimal_swagger_dict['definitions']['Address'] = address_spec
    ref_spec = {'$ref': '#/definitions/Address'}
    swagger_spec = Spec(minimal_swagger_dict)
    result = marshal_object(swagger_spec, ref_spec, address)
    assert address == result


def test_recursive_ref_with_depth_1(recursive_swagger_spec):
    result = marshal_object(
        recursive_swagger_spec,
        {'$ref': '#/definitions/Node'},
        {'name': 'foo', 'child': None},
    )
    assert result == {'name': 'foo'}


def test_recursive_ref_with_depth_n(recursive_swagger_spec):
    value = {
        'name': 'foo',
        'child': {
            'name': 'bar',
            'child': {
                'name': 'baz',
                'child': None,
            },
        },
    }
    result = marshal_object(
        recursive_swagger_spec,
        {'$ref': '#/definitions/Node'},
        value,
    )

    expected = {
        'name': 'foo',
        'child': {
            'name': 'bar',
            'child': {
                'name': 'baz',
            },
        },
    }
    assert result == expected


def test_marshal_with_nullable_required_property(empty_swagger_spec):
    object_spec = {
        'type': 'object',
        'required': ['x'],
        'properties': {
            'x': {
                'type': 'string',
                'x-nullable': True,
            },
        },
    }
    value = {'x': None}
    result = marshal_object(empty_swagger_spec, object_spec, value)
    assert result == value


def test_marshal_with_nullable_non_required_property(empty_swagger_spec):
    object_spec = {
        'type': 'object',
        'properties': {
            'x': {
                'type': 'string',
                'x-nullable': True,
            },
            'y': {
                'type': 'string',
                'x-nullable': True,
            },
        },
    }
    value = {'x': None}
    result = marshal_object(empty_swagger_spec, object_spec, value)
    assert result == value


def test_marshal_with_non_nullable_non_required_property(empty_swagger_spec):
    object_spec = {
        'type': 'object',
        'properties': {
            'x': {
                'type': 'string',
            },
        },
    }
    value = {'x': None}
    result = marshal_object(empty_swagger_spec, object_spec, value)
    assert result == {}


def test_marshal_object_polymorphic_specs(polymorphic_spec):
    list_of_pets_dict = {
        'number_of_pets': 2,
        'list': [
            {
                'name': 'a dog name',
                'type': 'Dog',
                'birth_date': datetime.date(2017, 3, 9),
            },
            {
                'name': 'a cat name',
                'type': 'Cat',
                'color': 'white',
            },
        ],
    }
    polymorphic_spec.config['use_models'] = False
    pet_list = marshal_object(
        swagger_spec=polymorphic_spec,
        object_spec=polymorphic_spec.spec_dict['definitions']['PetList'],
        object_value=list_of_pets_dict,
    )

    assert pet_list == {
        'number_of_pets': 2,
        'list': [
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
        ],
    }


@pytest.mark.parametrize(
    'additionalProperties, value, expected',
    [
        (
            None,
            {'property': None},
            {},
        ),
        (
            None,
            {'property': datetime.datetime(2018, 5, 21, tzinfo=tzutc())},
            {'property': '2018-05-21T00:00:00+00:00'},
        ),
        (
            {},
            {'property': datetime.datetime(2018, 5, 21, tzinfo=tzutc()), 'other': '2018-05-21'},
            {'property': '2018-05-21T00:00:00+00:00', 'other': '2018-05-21'},
        ),
        (
            True,
            {'property': datetime.datetime(2018, 5, 21, tzinfo=tzutc()), 'other': '2018-05-21'},
            {'property': '2018-05-21T00:00:00+00:00', 'other': '2018-05-21'},
        ),
        (
            False,
            # Mmarshaling does not do validation
            {'property': datetime.datetime(2018, 5, 21, tzinfo=tzutc()), 'other': '2018-05-21'},
            {'property': '2018-05-21T00:00:00+00:00', 'other': '2018-05-21'},
        ),
        (
            {'type': 'string', 'format': 'date'},
            {'property': datetime.datetime(2018, 5, 21, tzinfo=tzutc()), 'other': datetime.date(2018, 5, 21)},
            {'property': '2018-05-21T00:00:00+00:00', 'other': '2018-05-21'},
        ),
    ],
)
def test_marshal_object_with_additional_properties(minimal_swagger_dict, additionalProperties, value, expected):
    MyModel_spec = {
        'properties': {
            'property': {
                'type': 'string',
                'format': 'date-time',
            },
        },
        'type': 'object',
        'x-model': 'MyModel',
    }
    if additionalProperties is not None:
        MyModel_spec['additionalProperties'] = additionalProperties
    minimal_swagger_dict['definitions']['MyModel'] = MyModel_spec
    spec = Spec.from_dict(minimal_swagger_dict)
    assert marshal_object(spec, MyModel_spec, value) == expected
