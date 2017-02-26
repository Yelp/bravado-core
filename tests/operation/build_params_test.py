# -*- coding: utf-8 -*-
from bravado_core.operation import build_params
from bravado_core.operation import Operation
from bravado_core.spec import Spec


def test_no_params(minimal_swagger_dict):
    op_spec = {
        'operationId': 'get_all_pets',
        # op params would go here
        'responses': {
            '200': {
            }
        }
    }
    path_spec = {
        'get': op_spec
        # path params would go here
    }
    minimal_swagger_dict['paths']['/pets'] = path_spec
    swagger_spec = Spec(minimal_swagger_dict)
    op = Operation(swagger_spec, '/pets', 'get', op_spec)
    params = build_params(op)
    assert len(params) == 0


def test_op_param_only(minimal_swagger_dict):
    op_spec = {
        'operationId': 'get_pet_by_id',
        'parameters': [
            {
                'name': 'pet_id',
                'in': 'query',
                'required': 'true',
                'type': 'integer',
            }
        ],
        'responses': {
            '200': {
            }
        }
    }
    path_spec = {
        'get': op_spec,
        # path params would go here
    }
    minimal_swagger_dict['paths']['/pets'] = path_spec
    swagger_spec = Spec(minimal_swagger_dict)
    op = Operation(swagger_spec, '/pets', 'get', op_spec)
    params = build_params(op)
    assert len(params) == 1
    assert 'pet_id' in params


def test_path_param_only(minimal_swagger_dict):
    op_spec = {
        'operationId': 'get_pet_by_id',
        # op params would go here
        'responses': {
            '200': {
            }
        }
    }
    path_spec = {
        'get': op_spec,
        'parameters': [
            {
                'name': 'pet_id',
                'in': 'query',
                'required': 'true',
                'type': 'integer',
            }
        ],
    }
    minimal_swagger_dict['paths']['/pets'] = path_spec
    swagger_spec = Spec(minimal_swagger_dict)
    op = Operation(swagger_spec, '/pets', 'get', op_spec)
    params = build_params(op)
    assert len(params) == 1
    assert 'pet_id' in params


def test_path_param_and_op_param(minimal_swagger_dict):
    op_spec = {
        'operationId': 'get_pet_by_id',
        'parameters': [
            {
                'name': 'pet_id',
                'in': 'query',
                'required': True,
                'type': 'integer',
            }
        ],
        'responses': {
            '200': {
            }
        }
    }
    path_spec = {
        'get': op_spec,
        'parameters': [
            {
                'name': 'sort_key',
                'in': 'query',
                'required': False,
                'type': 'string',
            }
        ],
    }
    minimal_swagger_dict['paths']['/pets'] = path_spec
    swagger_spec = Spec(minimal_swagger_dict)
    op = Operation(swagger_spec, '/pets', 'get', op_spec)
    params = build_params(op)
    assert len(params) == 2
    assert 'pet_id' in params
    assert 'sort_key' in params


def test_op_param_overrides_path_param(minimal_swagger_dict):
    # Override 'required' to be True for the sort_key param
    op_spec = {
        'operationId': 'get_pet_by_id',
        'parameters': [
            {
                'name': 'sort_key',
                'in': 'query',
                'required': True,
                'type': 'string',
            }
        ],
        'responses': {
            '200': {
            }
        }
    }
    path_spec = {
        'get': op_spec,
        'parameters': [
            {
                'name': 'sort_key',
                'in': 'query',
                'required': False,
                'type': 'string',
            }
        ],
    }
    minimal_swagger_dict['paths']['/pets'] = path_spec
    swagger_spec = Spec(minimal_swagger_dict)
    op = Operation(swagger_spec, '/pets', 'get', op_spec)
    params = build_params(op)
    assert len(params) == 1
    assert 'sort_key' in params
    assert params['sort_key'].required


def test_path_param_and_op_param_refs(minimal_swagger_dict):
    # pet_id param is #/parameters/PetId
    # sort_key param is #/parameters/SortKey
    parameters = {
        'PetId': {
            'name': 'pet_id',
            'in': 'query',
            'required': True,
            'type': 'integer',
        },
        'SortKey': {
            'name': 'sort_key',
            'in': 'query',
            'required': False,
            'type': 'string',
        },
    }
    op_spec = {
        'operationId': 'get_pet_by_id',
        'parameters': [
            {'$ref': '#/parameters/PetId'},
        ],
        'responses': {
            '200': {
            }
        }
    }
    path_spec = {
        'get': op_spec,
        'parameters': [
            {'$ref': '#/parameters/SortKey'},
        ],
    }
    minimal_swagger_dict['paths']['/pets'] = path_spec
    minimal_swagger_dict['parameters'] = parameters
    swagger_spec = Spec(minimal_swagger_dict)
    op = Operation(swagger_spec, '/pets', 'get', op_spec)
    params = build_params(op)
    assert len(params) == 2
    assert 'pet_id' in params
    assert 'sort_key' in params
