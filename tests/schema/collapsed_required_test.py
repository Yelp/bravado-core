# -*- coding: utf-8 -*-
from bravado_core.schema import collapsed_required


def test_allOf(users_spec, users_swagger_spec):
    """Test allOf functionality, including:
     - multiple levels of allOf
     - multiple references within one allOf
     - referencing the same model multiple times across the
       allOf-hierarchy
    """
    superuser_spec = users_spec['SuperUser']
    required = collapsed_required(superuser_spec, users_swagger_spec)
    assert required == {'id', 'username', 'password', 'permissions'}
