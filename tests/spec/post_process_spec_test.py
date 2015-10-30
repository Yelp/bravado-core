import functools
import json

from mock import Mock

from bravado_core.spec import post_process_spec, Spec


def test_empty():
    swagger_spec = Spec({})
    callback = Mock()
    post_process_spec(swagger_spec, [callback])
    assert callback.call_count == 0


def test_single_key():
    spec_dict = {'definitions':{} }
    swagger_spec = Spec(spec_dict)
    callback = Mock()
    post_process_spec(swagger_spec, [callback])
    assert callback.call_count == 1
    callback.assert_called_once_with(spec_dict, 'definitions', ['definitions'])


def test_visits_refs_only_once():
    # bar should only be de-reffed once even though there are two refs to it
    spec_dict = {
        'ref_one': {'$ref': '#/bar'},
        'ref_two': {'$ref': '#/bar'},
        'bar': 'baz'
    }
    swagger_spec = Spec(spec_dict)

    # Yech! mock doesn't make this easy
    mutable = {'cnt': 0}

    def callback(container, key, path, mutable):
        # Bump the mutable counter every time bar is de-reffed
        if key == 'bar':
            mutable['cnt'] += 1

    post_process_spec(
        swagger_spec,
        [functools.partial(callback, mutable=mutable)])

    assert mutable['cnt'] == 1


# def test_dict():
#     swagger_dict = {
#         'foo': {
#             "$ref": "#/definitions/User"
#         },
#         'definitions': {
#             'User': {
#                 'properties': {
#                     'first_name': {
#                         'type': 'string'
#                     },
#                     'children': {
#                         'type': 'array',
#                         'items': {
#                             'type': {
#                                 '$ref': '#/definitions/User'
#                             }
#                         }
#                     }
#                 }
#             }
#         },
#         # 'another_file': {
#         #     'definitions': {
#         #         'User': {
#         #             'properties': {
#         #                 'first_name': {
#         #                     'type': 'string'
#         #                 },
#         #             }
#         #         }
#         #     }
#         # }
#     }
#
#     swagger_spec = Spec(swagger_dict)
#
#     def callback(container, key, path):
#         print container, key, path
#         # if len(path) >= 2 and path[-2] == 'definitions':
#         #     model_name = key
#         #     print 'Found model: %s' % model_name
#         #     if not model_name in visited_models:
#         #         model_spec = swagger_spec.resolve(container, key)
#         #         model_spec['x-model'] = model_name
#         #         visited_models[model_name] = path
#         #     else:
#         #         raise ValueError('Duplicate "{0}" model found at path {1}. '
#         #             'Original "{0}" model at path {2}'.format(
#         #             model_name, path, visited_models[model_name]))
#
#     post_process_spec(swagger_spec, [callback])
#     print json.dumps(swagger_dict, indent=2)
