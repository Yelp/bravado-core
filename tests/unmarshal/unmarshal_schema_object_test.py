# -*- coding: utf-8 -*-
import pytest

from bravado_core.spec import Spec
from bravado_core.unmarshal import unmarshal_schema_object


@pytest.mark.xfail(run=False)
def test_use_models_true(petstore_dict):
    petstore_spec = Spec.from_dict(petstore_dict, config={'use_models': True})
    Category = petstore_spec.definitions['Category']
    category_spec = petstore_spec.spec_dict['definitions']['Category']

    result = unmarshal_schema_object(
        petstore_spec,
        category_spec,
        {'id': 200, 'name': 'short-hair'})

    assert isinstance(result, Category)


@pytest.mark.xfail(run=False)
def test_use_models_false(petstore_dict):
    petstore_spec = Spec.from_dict(petstore_dict, config={'use_models': False})
    category_spec = petstore_spec.spec_dict['definitions']['Category']

    result = unmarshal_schema_object(
        petstore_spec,
        category_spec,
        {'id': 200, 'name': 'short-hair'})

    assert isinstance(result, dict)
