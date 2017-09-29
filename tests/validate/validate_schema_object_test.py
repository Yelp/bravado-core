# -*- coding: utf-8 -*-
import pytest

from bravado_core.exception import SwaggerMappingError
from bravado_core.validate import validate_schema_object


def test_unknown_type(minimal_swagger_spec):
    with pytest.raises(SwaggerMappingError) as excinfo:
        validate_schema_object(minimal_swagger_spec, {'type': 'unknown'}, 'foo')
    assert 'Unknown type' in str(excinfo.value)


def test_allOf_with_ref(composition_spec):
    pongclone_spec = composition_spec.spec_dict['definitions']['pongClone']
    value = {
        'additionalFeature': 'Badges',
        'gameSystem': 'NES',
        'pang': 'value',
        'releaseDate': 'October',
    }
    validate_schema_object(composition_spec, pongclone_spec, value)


def test_no_validation_when_no_type(minimal_swagger_spec):
    validate_schema_object(minimal_swagger_spec, {}, None)
