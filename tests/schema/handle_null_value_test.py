# -*- coding: utf-8 -*-
import pytest

from bravado_core.exception import SwaggerMappingError
from bravado_core.schema import handle_null_value


def test_default(empty_swagger_spec):
    spec = {
        'type': 'integer',
        'default': 42
    }

    assert 42 == handle_null_value(empty_swagger_spec, spec)


def test_nullable(empty_swagger_spec):
    spec = {
        'type': 'integer',
        'x-nullable': True,
    }

    assert None is handle_null_value(empty_swagger_spec, spec)


def test_raise(empty_swagger_spec):
    spec = {
        'type': 'integer',
    }

    with pytest.raises(SwaggerMappingError):
        handle_null_value(empty_swagger_spec, spec)
