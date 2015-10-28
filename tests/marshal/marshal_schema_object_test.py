import copy

import pytest

from bravado_core.exception import SwaggerMappingError
from bravado_core.marshal import marshal_schema_object
from bravado_core.spec import Spec


@pytest.mark.xfail(run=False)
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
