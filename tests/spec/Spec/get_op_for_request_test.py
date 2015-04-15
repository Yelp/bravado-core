def test_found(petstore_spec):
    op = petstore_spec.get_op_for_request('GET', '/pet/{petId}')
    assert op == petstore_spec.resources['pet'].operations['getPetById']


def test_not_found(petstore_spec):
    op = petstore_spec.get_op_for_request('GET', '/foo/{fooId}')
    assert op is None
