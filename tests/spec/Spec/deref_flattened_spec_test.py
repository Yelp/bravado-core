# -*- coding: utf-8 -*-
from six import iterkeys
from six import itervalues
from typing import Any

from bravado_core.schema import is_dict_like
from bravado_core.schema import is_list_like
from bravado_core.spec import Spec
from tests.conftest import get_url


def _get_model(spec_dict, model_name):
    for model_schema in itervalues(spec_dict['definitions']):
        if model_schema.get('x-model') == model_name:
            return model_schema


def _equivalent(spec, obj1, obj2):
    # type: (Spec, Any, Any) -> bool
    if is_dict_like(obj1) != is_dict_like(obj2) or is_list_like(obj1) != is_list_like(obj2):
        return False

    if is_dict_like(obj1):
        if len(obj1) != len(obj2):
            return False

        for key in iterkeys(obj1):
            if key not in obj2:
                return False
            if not _equivalent(spec, spec._force_deref(obj1[key]), spec._force_deref(obj2[key])):
                return False
        return True

    elif is_list_like(obj1):
        if len(obj1) != len(obj2):
            return False

        for key in range(len(obj1)):
            if not _equivalent(spec, spec._force_deref(obj1[key]), spec._force_deref(obj2[key])):
                return False
        return True
    else:
        return obj1 == obj2


def test_deref_flattened_spec_not_recursive_specs(petstore_spec):
    spec_dict = petstore_spec.spec_dict
    deref_spec_dict = petstore_spec.deref_flattened_spec

    # NOTE: Pet spec is not recursive
    pet_spec = _get_model(spec_dict, 'Pet')
    deref_pet_spec = _get_model(deref_spec_dict, 'Pet')

    # property 'category' is different because it is a reference
    assert pet_spec['properties']['category'] != deref_pet_spec['properties']['category']

    # dereferencing category the two parameter specs are equivalent
    assert petstore_spec._force_deref(pet_spec['properties']['category']) == deref_pet_spec['properties']['category']

    assert _equivalent(petstore_spec, pet_spec, deref_pet_spec)
    assert _equivalent(petstore_spec, petstore_spec.spec_dict, petstore_spec.deref_flattened_spec)


def test_deref_flattened_spec_recursive_specs(multi_file_recursive_spec):
    deref_spec_dict = multi_file_recursive_spec.deref_flattened_spec

    ping = _get_model(deref_spec_dict, 'ping')
    assert id(ping) == id(ping['properties']['pong']['properties']['ping'])
    assert id(ping['properties']['pong']) == id(ping['properties']['pong']['properties']['ping']['properties']['pong'])

    pong = _get_model(deref_spec_dict, 'pong')
    assert id(pong) == id(pong['properties']['ping']['properties']['pong'])
    assert id(pong['properties']['ping']) == id(pong['properties']['ping']['properties']['pong']['properties']['ping'])


def test_build_spec_object_with_recursive_specs_and_fully_dereference(
    multi_file_recursive_dict, multi_file_recursive_abspath,
):
    # Test pass if spec object is built
    assert Spec.from_dict(
        spec_dict=multi_file_recursive_dict,
        origin_url=get_url(multi_file_recursive_abspath),
        config={
            'internally_dereference_refs': True,
        },
    ).api_url.startswith('file:')
