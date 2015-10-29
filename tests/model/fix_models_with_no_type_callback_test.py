# import pytest
#
# from jsonref import JsonRef
#
# from bravado_core.model import fix_models_with_no_type_callback, MODEL_MARKER
#
#
# @pytest.fixture
# def pet_model_spec():
#     return {
#         MODEL_MARKER: 'Pet',
#         'properties': {
#             'name': {
#                 'type': 'string'
#             }
#         }
#     }
#
#
# @pytest.fixture
# def response_spec():
#     return {
#         'description': 'A pet',
#         'schema': 'Unit test will fill in this value'
#     }
#
#
# def test_inserts_missing_type(response_spec, pet_model_spec):
#     ref_obj = {'$ref': '#/definitions/Pet'}
#     pet_proxy = JsonRef(ref_obj)
#     pet_proxy.__subject__ = pet_model_spec
#     response_spec['schema'] = pet_proxy
#     fix_models_with_no_type_callback(response_spec, key='schema')
#     assert pet_model_spec['type'] == 'object'
#
#
# def test_noop_when_not_jsonref(response_spec, pet_model_spec):
#     response_spec['schema'] = pet_model_spec
#     fix_models_with_no_type_callback(response_spec, key='schema')
#     assert 'type' not in pet_model_spec
#
#
# def test_noop_when_type_is_object(response_spec, pet_model_spec):
#     response_spec['schema'] = pet_model_spec
#     pet_model_spec['type'] = 'object'
#     fix_models_with_no_type_callback(response_spec, key='schema')
#     assert pet_model_spec['type'] == 'object'
