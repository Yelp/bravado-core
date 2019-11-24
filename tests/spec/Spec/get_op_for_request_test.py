# -*- coding: utf-8 -*-
from bravado_core.spec import Spec


def test_found_with_no_basepath(petstore_dict):
    del petstore_dict['basePath']
    petstore_spec = Spec.from_dict(petstore_dict)
    op = petstore_spec.get_op_for_request('GET', '/pet/{petId}')
    assert op == petstore_spec.resources['pet'].operations['getPetById']


def test_not_found_with_no_basepath(petstore_dict):
    del petstore_dict['basePath']
    petstore_spec = Spec.from_dict(petstore_dict)
    op = petstore_spec.get_op_for_request('GET', '/foo/{fooId}')
    assert op is None


def test_found_with_basepath(petstore_spec, getPetByIdPetstoreOperation):
    op = petstore_spec.get_op_for_request('GET', '/v2/pet/{petId}')
    assert op == getPetByIdPetstoreOperation


def test_found_with_basepath_containing_trailing_slash(petstore_dict):
    petstore_dict['basePath'] = '/v2/'
    petstore_spec = Spec.from_dict(petstore_dict)
    op = petstore_spec.get_op_for_request('GET', '/v2/pet/{petId}')
    assert op == petstore_spec.resources['pet'].operations['getPetById']


def test_not_found_with_basepath(petstore_spec):
    op = petstore_spec.get_op_for_request('GET', '/v2/foo/{fooId}')
    assert op is None
