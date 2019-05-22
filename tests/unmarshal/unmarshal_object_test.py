# -*- coding: utf-8 -*-
import copy
import datetime

import pytest
from dateutil.tz import tzutc

from bravado_core.exception import SwaggerMappingError
from bravado_core.spec import Spec
from bravado_core.unmarshal import unmarshal_object


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
                'default': 'Street',
            },
        },
    }


@pytest.fixture
def business_address_spec():
    return {
        'allOf': [
            {
                '$ref': '#/definitions/Address',
            },
            {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string',
                    },
                    'floor': {
                        'type': 'integer',
                        'x-nullable': True,
                    },
                },
            },
        ],
    }


@pytest.fixture
def location_spec():
    return {
        'type': 'object',
        'required': ['longitude', 'latitude'],
        'properties': {
            'longitude': {
                'type': 'number',
            },
            'latitude': {
                'type': 'number',
            },
        },
    }


@pytest.fixture
def business_address_swagger_dict(minimal_swagger_dict, address_spec, business_address_spec):
    minimal_swagger_dict['definitions']['Address'] = address_spec
    minimal_swagger_dict['definitions']['BusinessAddress'] = business_address_spec

    business_address_response = {
        'get': {
            'responses': {
                '200': {
                    'description': 'A business address',
                    'schema': {
                        '$ref': '#/definitions/BusinessAddress',
                    },
                },
            },
        },
    }
    minimal_swagger_dict['paths']['/foo'] = business_address_response
    return minimal_swagger_dict


@pytest.fixture(
    params=[
        {'include_missing_properties': True},
        {'include_missing_properties': False},
    ],
)
def business_address_swagger_spec(request, business_address_swagger_dict):
    return Spec.from_dict(business_address_swagger_dict, config=request.param)


@pytest.fixture
def address():
    return {
        'number': 1600,
        'street_name': u'Ümlaut',
        'street_type': 'Avenue',
    }


@pytest.mark.parametrize(
    'street_type, expected_street_type',
    (
        ('Avenue', 'Avenue'),
        (None, 'Street'),  # make sure the default works
    ),
)
def test_with_properties(empty_swagger_spec, address_spec, address, street_type, expected_street_type):
    address['street_type'] = street_type
    expected_address = {
        'number': 1600,
        'street_name': u'Ümlaut',
        'street_type': expected_street_type,
    }
    result = unmarshal_object(empty_swagger_spec, address_spec, address)
    assert expected_address == result


def test_missing_with_default(empty_swagger_spec, address_spec, address):
    del address['street_type']
    expected_address = {
        'number': 1600,
        'street_name': u'Ümlaut',
        'street_type': 'Street',
    }
    result = unmarshal_object(empty_swagger_spec, address_spec, address)
    assert expected_address == result


def test_with_array(empty_swagger_spec, address_spec):
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


def test_with_model_composition(business_address_swagger_spec, address_spec, business_address_spec):
    business_address_dict = {
        'company': 'n/a',
        'number': 1600,
        'street_name': 'Pennsylvania',
        'street_type': 'Avenue',
    }
    expected_business_address = {
        'company': 'n/a',
        'number': 1600,
        'street_name': 'Pennsylvania',
        'street_type': 'Avenue',
    }

    if business_address_swagger_spec.config['include_missing_properties']:
        expected_business_address.update(floor=None, name=None)

    business_address = unmarshal_object(
        business_address_swagger_spec, business_address_spec,
        business_address_dict,
    )
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


def test_self_property_with_model(minimal_swagger_dict):
    link_spec = {
        'type': 'object',
        'required': ['_links'],
        'properties': {
            '_links': {
                '$ref': '#/definitions/Self',
            },
        },
    }

    self_spec = {
        'type': 'object',
        'required': ['self'],
        'properties': {
            'self': {
                'type': 'object',
                'required': ['href'],
                'properties': {
                    'href': {
                        'type': 'string',
                    },
                },
            },
        },
    }

    minimal_swagger_dict['definitions']['Links'] = link_spec
    minimal_swagger_dict['definitions']['Self'] = self_spec

    self_link_response = {
        'get': {
            'responses': {
                '200': {
                    'description': 'A self link.',
                    'schema': {
                        '$ref': '#/definitions/Links',
                    },
                },
            },
        },
    }
    minimal_swagger_dict['paths']['/foo'] = self_link_response

    self_link_swagger_spec = Spec.from_dict(minimal_swagger_dict)

    href = "http://example.com"
    self_link_dict = {
        "_links": {
            "self": {
                "href": href,
            },
        },
    }

    self_link = unmarshal_object(self_link_swagger_spec, link_spec, self_link_dict)
    assert self_link["_links"].self["href"] == href


def test_object_not_dict_like_raises_error(empty_swagger_spec, address_spec):
    i_am_not_dict_like = 34
    with pytest.raises(SwaggerMappingError) as excinfo:
        unmarshal_object(empty_swagger_spec, address_spec, i_am_not_dict_like)
    assert 'Expected dict' in str(excinfo.value)


def test_mising_properties_set_to_None(empty_swagger_spec, address_spec, address):
    del address['street_name']
    expected_address = {
        'number': 1600,
        'street_name': None,
        'street_type': 'Avenue',
    }
    result = unmarshal_object(empty_swagger_spec, address_spec, address)
    assert expected_address == result


def test_pass_through_additionalProperties_with_no_spec(empty_swagger_spec, address_spec, address):
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


def test_pass_through_property_with_no_spec(empty_swagger_spec, address_spec, address):
    del address_spec['properties']['street_name']['type']
    result = unmarshal_object(empty_swagger_spec, address_spec, address)
    assert result == address


def test_pass_through_null_property_with_no_spec(empty_swagger_spec, address_spec, address):
    address['no_spec_field'] = None
    result = unmarshal_object(empty_swagger_spec, address_spec, address)
    assert result == address


def test_recursive_ref_with_depth_1(recursive_swagger_spec):
    result = unmarshal_object(
        recursive_swagger_spec,
        {'$ref': '#/definitions/Node'},
        {'name': 'foo'},
    )
    assert result == {'name': 'foo', 'date': None, 'child': None}


def test_recursive_ref_with_depth_n(recursive_swagger_spec):
    result = unmarshal_object(
        recursive_swagger_spec,
        {'$ref': '#/definitions/Node'},
        {
            'name': 'foo',
            'date': '2019-05-01',
            'child': {
                'name': 'bar',
                'date': '2019-05-02',
                'child': {
                    'name': 'baz',
                },
            },
        },
    )
    assert result == {
        'name': 'foo',
        'date': datetime.date(2019, 5, 1),
        'child': {
            'name': 'bar',
            'date': datetime.date(2019, 5, 2),
            'child': {
                'name': 'baz',
                'date': None,
                'child': None,
            },
        },
    }


def nullable_spec_factory(required, nullable, property_type):
    content_spec = {
        'type': 'object',
        'required': ['x'] if required else [],
        'properties': {
            'x': {
                'type': property_type,
                'x-nullable': nullable,
            },
        },
    }
    if property_type == 'array':
        content_spec['properties']['x']['items'] = {'type': 'string'}
    return content_spec


@pytest.mark.parametrize('nullable', [True, False])
@pytest.mark.parametrize('required', [True, False])
@pytest.mark.parametrize(
    'property_type, value',
    [
        ('string', 'y'),
        ('object', {'y': 'z'}),
        ('array', ['one', 'two', 'three']),
    ],
)
def test_nullable_with_value(
    empty_swagger_spec, nullable, required,
    property_type, value,
):
    content_spec = nullable_spec_factory(required, nullable, property_type)
    obj = {'x': value}
    expected = copy.deepcopy(obj)
    result = unmarshal_object(empty_swagger_spec, content_spec, obj)
    assert expected == result


@pytest.mark.parametrize('nullable', [True, False])
@pytest.mark.parametrize('property_type', ['string', 'object', 'array'])
def test_nullable_no_value(empty_swagger_spec, nullable, property_type):
    content_spec = nullable_spec_factory(
        required=False,
        nullable=nullable,
        property_type=property_type,
    )
    value = {}
    result = unmarshal_object(empty_swagger_spec, content_spec, value)
    assert result == {'x': None}  # Missing parameters are re-introduced


@pytest.mark.parametrize('required', [True, False])
@pytest.mark.parametrize('property_type', ['string', 'object', 'array'])
def test_nullable_none_value(empty_swagger_spec, required, property_type):
    content_spec = nullable_spec_factory(
        required=required,
        nullable=True,
        property_type=property_type,
    )
    value = {'x': None}
    result = unmarshal_object(empty_swagger_spec, content_spec, value)
    assert result == {'x': None}


@pytest.mark.parametrize('property_type', ['string', 'object', 'array'])
def test_non_nullable_none_value(empty_swagger_spec, property_type):
    content_spec = nullable_spec_factory(
        required=True,
        nullable=False,
        property_type=property_type,
    )
    value = {'x': None}
    with pytest.raises(SwaggerMappingError) as excinfo:
        unmarshal_object(empty_swagger_spec, content_spec, value)
    assert 'is a required value' in str(excinfo.value)


@pytest.mark.parametrize('property_type', ['string', 'object', 'array'])
def test_non_required_none_value(empty_swagger_spec, property_type):
    content_spec = nullable_spec_factory(
        required=False,
        nullable=False,
        property_type=property_type,
    )
    value = {'x': None}
    result = unmarshal_object(empty_swagger_spec, content_spec, value)
    assert result == {'x': None}


def test_unmarshal_object_polymorphic_specs(polymorphic_spec):
    list_of_pets_dict = {
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
    polymorphic_spec.config['use_models'] = False
    pet_list = unmarshal_object(
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
                'birth_date': datetime.date(2017, 3, 9),
            },
            {
                'name': 'a cat name',
                'type': 'Cat',
                'color': 'white',
            },
        ]
    }


@pytest.mark.parametrize(
    'additionalProperties, value, expected',
    [
        (
            None,
            {},
            {'property': None},
        ),
        (
            None,
            {'property': '2018-05-21T00:00:00+00:00'},
            {'property': datetime.datetime(2018, 5, 21, tzinfo=tzutc())},
        ),
        (
            {},
            {'property': '2018-05-21T00:00:00+00:00', 'other': '2018-05-21'},
            {'property': datetime.datetime(2018, 5, 21, tzinfo=tzutc()), 'other': '2018-05-21'},
        ),
        (
            True,
            {'property': '2018-05-21T00:00:00+00:00', 'other': '2018-05-21'},
            {'property': datetime.datetime(2018, 5, 21, tzinfo=tzutc()), 'other': '2018-05-21'},
        ),
        pytest.param(
            False,
            {'property': '2018-05-21T00:00:00+00:00', 'other': '2018-05-21'},
            # Unmarshaling does not do validation
            {'property': datetime.datetime(2018, 5, 21, tzinfo=tzutc()), 'other': '2018-05-21'},
            marks=pytest.mark.xfail(reason='Unmarshaling should not perform validation, but this is the case for now'),
        ),
        (
            {'type': 'string', 'format': 'date'},
            {'property': '2018-05-21T00:00:00+00:00', 'other': '2018-05-21'},
            {'property': datetime.datetime(2018, 5, 21, tzinfo=tzutc()), 'other': datetime.date(2018, 5, 21)},
        ),
    ],
)
def test_unmarshal_object_with_additional_properties(minimal_swagger_dict, additionalProperties, value, expected):
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
    MyModel = spec.definitions['MyModel']
    assert MyModel._unmarshal(value)._as_dict() == expected


def test_default_with_format(empty_swagger_spec):
    result = unmarshal_object(
        empty_swagger_spec,
        {
            'type': 'object',
            'properties': {
                'item': {
                    'type': 'string',
                    'format': 'date',
                },
            },
            'default': {'item': '2019-05-22'},
        },
        None,
    )
    assert {'item': datetime.date(2019, 5, 22)} == result
