from bravado_core.resource import convert_path_to_resource


def test_success():
    path_names = [
        '/pet',
        '/pet/findByStatus',
        '/pet/findByTags',
        '/pet/{petId}']
    for path_name in path_names:
        assert 'pet' == convert_path_to_resource(path_name)


def test_root_path():
    assert convert_path_to_resource('/') == '_'
