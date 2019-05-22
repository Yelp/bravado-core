# -*- coding: utf-8 -*-
import copy
import datetime
from collections import defaultdict

import pytest

from bravado_core.exception import SwaggerMappingError
from bravado_core.marshal import marshal_schema_object
from bravado_core.spec import Spec


def test_dicts_can_be_used_instead_of_models(petstore_dict):
    petstore_spec = Spec.from_dict(petstore_dict)
    pet_spec = petstore_spec.spec_dict['definitions']['Pet']
    pet = {
        'id': 1,
        'name': 'Fido',
        'status': 'sold',
        'photoUrls': ['wagtail.png', 'bark.png'],
        'category': {
            'id': 200,
            'name': 'friendly',
        },
        'tags': [
            {'id': 99, 'name': 'mini'},
            {'id': 100, 'name': 'brown'},
        ],
    }
    expected = copy.deepcopy(pet)
    result = marshal_schema_object(petstore_spec, pet_spec, pet)
    assert expected == result


def test_defaultdicts_can_be_used_instead_of_models(petstore_dict):
    petstore_spec = Spec.from_dict(petstore_dict)
    pet_spec = petstore_spec.spec_dict['definitions']['Pet']
    pet = defaultdict(
        None, {
            'id': 1,
            'name': 'Fido',
            'status': 'sold',
            'photoUrls': ['wagtail.png', 'bark.png'],
            'category': {
                'id': 200,
                'name': 'friendly',
            },
            'tags': [
                {'id': 99, 'name': 'mini'},
                {'id': 100, 'name': 'brown'},
            ],
        },
    )
    expected = copy.deepcopy(pet)
    result = marshal_schema_object(petstore_spec, pet_spec, pet)
    assert expected == result


def test_unknown_type_raises_error(empty_swagger_spec):
    invalid_spec = {'type': 'foo'}
    with pytest.raises(SwaggerMappingError) as excinfo:
        marshal_schema_object(empty_swagger_spec, invalid_spec, "don't matter")
    assert 'Unknown type foo' in str(excinfo.value)


def test_ref(minimal_swagger_dict):
    ref_spec = {'$ref': '#/refs/Foo'}
    foo_spec = {'type': 'string'}
    minimal_swagger_dict['refs'] = {'Foo': foo_spec}
    swagger_spec = Spec(minimal_swagger_dict)
    assert 'foo' == marshal_schema_object(swagger_spec, ref_spec, 'foo')


def test_marshal_raises_SwaggerMappingError_if_SwaggerFormat_fails_during_to_wire(minimal_swagger_dict):
    minimal_swagger_dict['definitions']['test'] = {
        'properties': {
            'date': {
                'type': 'string',
                'format': 'date',
            },
        },
        'required': [
            'date',
        ],
        'type': 'object',
    }
    swagger_spec = Spec(minimal_swagger_dict)
    date_str = datetime.date.today().isoformat()
    with pytest.raises(SwaggerMappingError) as excinfo:
        marshal_schema_object(
            swagger_spec=swagger_spec,
            schema_object_spec=minimal_swagger_dict['definitions']['test'],
            value={'date': date_str},
        )
    message, wrapped_exception = excinfo.value.args
    assert message == 'Error while marshalling value={} to type=string/date.'.format(date_str)
    assert type(wrapped_exception) is AttributeError
    assert wrapped_exception.args == ('\'str\' object has no attribute \'isoformat\'', )


def test_allOf_with_ref(composition_spec):
    pongclone_spec = composition_spec.spec_dict['definitions']['pongClone']
    value = {
        'additionalFeature': 'Badges',
        'gameSystem': 'NES',
        'pang': 'value',
        'releaseDate': 'October',
    }
    expected = copy.deepcopy(value)
    assert expected == marshal_schema_object(composition_spec, pongclone_spec, value)
