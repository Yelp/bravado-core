import pytest

from bravado_core.exception import SwaggerMappingError
from bravado_core.validate import validate_schema_object


def test_unknown_type(minimal_swagger_spec):
    with pytest.raises(SwaggerMappingError) as excinfo:
        validate_schema_object(minimal_swagger_spec, {'type': 'unknown'}, 'foo')
    assert 'Unknown type' in str(excinfo.value)
