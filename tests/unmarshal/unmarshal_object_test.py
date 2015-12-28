# -*- coding: utf-8 -*-
import pytest

from bravado_core.exception import SwaggerMappingError
from bravado_core.unmarshal import unmarshal_object
from bravado_core.spec import Spec


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
                    'Boulevard']
            }
        }
    }


@pytest.fixture
def location_spec():
    return {
        'type': 'object',
        'required': ['longitude', 'latitude'],
        'properties': {
            'longitude': {
                'type': 'number'
            },
            'latitude': {
                'type': 'number'
            },
        }
    }


@pytest.fixture
def address():
    return {
        'number': 1600,
        'street_name': u'Ümlaut',
        'street_type': 'Avenue'
    }


def test_with_properties(empty_swagger_spec, address_spec, address):
    expected_address = {
        'number': 1600,
        'street_name': u'Ümlaut',
        'street_type': 'Avenue'
    }
    result = unmarshal_object(empty_swagger_spec, address_spec, address)
    assert expected_address == result


def test_with_array(empty_swagger_spec, address_spec):
    tags_spec = {
        'type': 'array',
        'items': {
            'type': 'string'
        }
    }
    address_spec['properties']['tags'] = tags_spec
    address = {
        'number': 1600,
        'street_name': 'Pennsylvania',
        'street_type': 'Avenue',
        'tags': [
            'home',
            'best place on earth',
            'cul de sac'
        ],
    }
    result = unmarshal_object(empty_swagger_spec, address_spec, address)
    assert result == address


def test_with_nested_object(empty_swagger_spec, address_spec, location_spec):
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
    result = unmarshal_object(empty_swagger_spec, address_spec, address)
    assert result == address


def test_with_ref(minimal_swagger_dict, address_spec, location_spec):
    minimal_swagger_dict['definitions']['Location'] = location_spec
    address_spec['properties']['location'] = {'$ref': '#/definitions/Location'}
    address = {
        'number': 1600,
        'street_name': 'Pennsylvania',
        'street_type': 'Avenue',
        'location': {
            'longitude': 100.1,
            'latitude': 99.9,
        },
    }
    minimal_swagger_spec = Spec(minimal_swagger_dict)
    result = unmarshal_object(minimal_swagger_spec, address_spec, address)
    assert result == address


def test_with_poly_model(minimal_swagger_dict, address_spec):

    bus_address_spec = {
        'type': 'object',
        'allOf': [
            {
                '$ref': '#/definitions/Address'
            },
            {
                'properties': {
                    'name': {
                        'type': 'string'
                    }
                }
            }
        ]
    }

    minimal_swagger_dict['definitions']['Address'] = address_spec
    minimal_swagger_dict['definitions']['BusinessAddress'] = bus_address_spec

    business_address_response = {
        'get': {
            'responses': {
                '200': {
                    'description': 'A business address',
                    'schema': {
                        '$ref': '#/definitions/BusinessAddress',
                    }
                }
            }
        }
    }
    minimal_swagger_dict['paths']['/foo'] = business_address_response

    swagger_spec = Spec.from_dict(minimal_swagger_dict)

    address_dict = {
        'company': 'n/a',
        'number': 1600,
        'street_name': 'Pennsylvania',
        'street_type': 'Avenue'
    }
    expected_address = {
        'company': 'n/a',
        'number': 1600,
        'street_name': 'Pennsylvania',
        'street_type': 'Avenue'
    }

    address = unmarshal_object(swagger_spec, address_spec, address_dict)
    assert expected_address == address

    business_address_dict = {
        'company': 'n/a',
        'number': 1600,
        'street_name': 'Pennsylvania',
        'street_type': 'Avenue'
    }
    expected_business_address = {
        'company': 'n/a',
        'number': 1600,
        'name': None,
        'street_name': 'Pennsylvania',
        'street_type': 'Avenue'
    }

    business_address = unmarshal_object(swagger_spec, bus_address_spec,
                                        business_address_dict)
    assert expected_business_address == business_address


def test_with_model(minimal_swagger_dict, address_spec, location_spec):
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
                    }
                }
            }
        }
    }
    minimal_swagger_dict['paths']['/foo'] = location_response

    swagger_spec = Spec.from_dict(minimal_swagger_dict)
    address_spec['properties']['location'] = \
        swagger_spec.spec_dict['definitions']['Location']
    Location = swagger_spec.definitions['Location']

    address_dict = {
        'number': 1600,
        'street_name': 'Pennsylvania',
        'street_type': 'Avenue',
        'location': {
            'longitude': 100.1,
            'latitude': 99.9,
        },
    }
    expected_address = {
        'number': 1600,
        'street_name': 'Pennsylvania',
        'street_type': 'Avenue',
        'location': Location(longitude=100.1, latitude=99.9),
    }

    address = unmarshal_object(swagger_spec, address_spec, address_dict)
    assert expected_address == address


def test_object_not_dict_like_raises_error(empty_swagger_spec, address_spec):
    i_am_not_dict_like = 34
    with pytest.raises(SwaggerMappingError) as excinfo:
        unmarshal_object(empty_swagger_spec, address_spec, i_am_not_dict_like)
    assert 'Expected dict' in str(excinfo.value)


def test_mising_properties_set_to_None(
        empty_swagger_spec, address_spec, address):
    del address['street_name']
    expected_address = {
        'number': 1600,
        'street_name': None,
        'street_type': 'Avenue'
    }
    result = unmarshal_object(empty_swagger_spec, address_spec, address)
    assert expected_address == result


def test_pass_through_additionalProperties_with_no_spec(
        empty_swagger_spec, address_spec, address):
    address_spec['additionalProperties'] = True
    address['city'] = 'Swaggerville'
    expected_address = {
        'number': 1600,
        'street_name': u'Ümlaut',
        'street_type': 'Avenue',
        'city': 'Swaggerville',
    }
    result = unmarshal_object(empty_swagger_spec, address_spec, address)
    assert expected_address == result


def test_recursive_ref_with_depth_1(recursive_swagger_spec):
    result = unmarshal_object(
        recursive_swagger_spec,
        {'$ref': '#/definitions/Node'},
        {'name': 'foo'})
    assert result == {'name': 'foo', 'child': None}


def test_recursive_ref_with_depth_n(recursive_swagger_spec):
    value = {
        'name': 'foo',
        'child': {
            'name': 'bar',
            'child': {
                'name': 'baz'
            }
        }
    }
    result = unmarshal_object(
        recursive_swagger_spec,
        {'$ref': '#/definitions/Node'},
        value)

    expected = {
        'name': 'foo',
        'child': {
            'name': 'bar',
            'child': {
                'name': 'baz',
                'child': None
            }
        }
    }
    assert result == expected
