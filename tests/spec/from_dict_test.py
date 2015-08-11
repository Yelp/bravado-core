import mock

from bravado_core.spec import Spec


def test_definitions_not_present(minimal_swagger_dict):
    del minimal_swagger_dict['definitions']
    spec = Spec.from_dict(minimal_swagger_dict)
    assert 0 == len(spec.definitions)


@mock.patch('jsonref.JsonRef')
@mock.patch('bravado_core.spec.replace_jsonref_proxies')
@mock.patch.object(Spec, 'build')
def test_origin_uri_gets_passed_to_jsonref(mock_build, mock_prox, mock_ref,
                                           minimal_swagger_dict):
    Spec.from_dict(minimal_swagger_dict, origin_url='file:///foo')
    mock_ref.replace_refs.assert_called_once_with(
        minimal_swagger_dict, base_uri='file:///foo')
