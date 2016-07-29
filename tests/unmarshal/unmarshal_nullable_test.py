import pytest

from bravado_core.unmarshal import unmarshal_schema_object
from bravado_core.validate import validate_schema_object
from jsonschema.exceptions import ValidationError


"""If the value is a primitive, validation should pass if
`x-nullable` is `True` and the value is `None`. `required` is not
possible in this scenario.

+---------------------+------------------+
| x-nullable == False | 'x'  -> pass (1) |
|                     | None -> fail (2) |
+---------------------+------------------+
| x-nullable == True  | 'x'  -> pass (3) |
|                     | None -> pass (4) |
+---------------------+------------------+
"""


@pytest.mark.parametrize(['nullable', 'value'],
                         [(False, 'x'), (True, 'x'), (True, None)])
def test_unmarshal_with_primitive_pass(empty_swagger_spec, value, nullable):
    """Test scenarios in which validation should pass: (1), (3), (4)"""
    content_spec = {
        'type': 'string',
        'x-nullable': nullable,
    }
    validate_schema_object(empty_swagger_spec, content_spec, value)
    result = unmarshal_schema_object(empty_swagger_spec, content_spec, value)
    assert result == value


def test_unmarshal_with_primitive_fail(empty_swagger_spec):
    """Test scenarios in which validation should fail: (2)"""
    content_spec = {
        'type': 'string',
        'x-nullable': False,
    }
    value = None
    with pytest.raises(ValidationError) as excinfo:
        validate_schema_object(empty_swagger_spec, content_spec, value)
        unmarshal_schema_object(empty_swagger_spec, content_spec, value)
    assert excinfo.value.message == "None is not of type 'string'"


"""If the value is an object, validation should pass if
`x-nullable` is `True` and the value is `None`. `required` doesn't
have an influence.

+---------------------+-------------------------+--------------------------+
|                     | required == False       | required == True         |
+---------------------+-------------------------+--------------------------+
| x-nullable == False | {}          -> pass (1) | {}          -> fail  (4) |
|                     | {'x': 'y'}  -> pass (2) | {'x': 'y'}  -> pass  (5) |
|                     | {'x': None} -> fail (3) | {'x': None} -> fail  (6) |
+---------------------+-------------------------+--------------------------+
| x-nullable == True  | {}          -> pass (7) | {}          -> fail (10) |
|                     | {'x': 'y'}  -> pass (8) | {'x': 'y'}  -> pass (11) |
|                     | {'x': None} -> pass (9) | {'x': None} -> pass (12) |
+---------------------+-------------------------+--------------------------+
"""


def content_spec_factory(required, nullable):
    return {
        'type': 'object',
        'required': ['x'] if required else [],
        'properties': {
            'x': {
                'type': 'string',
                'x-nullable': nullable,
            }
        }
    }


@pytest.mark.parametrize('nullable', [True, False])
@pytest.mark.parametrize('required', [True, False])
def test_unmarshal_with_object_default(empty_swagger_spec, nullable, required):
    """With a value set, validation should always pass: (2), (5), (8), (11)"""
    content_spec = content_spec_factory(required, nullable)
    value = {'x': 'y'}

    validate_schema_object(empty_swagger_spec, content_spec, value)
    result = unmarshal_schema_object(empty_swagger_spec, content_spec, value)
    assert result == value


@pytest.mark.parametrize('nullable', [True, False])
def test_unmarshal_with_object_req_no_value(empty_swagger_spec, nullable):
    """When the value is required but not set at all, validation
    should fail: (4), (10)
    """
    content_spec = content_spec_factory(True, nullable)
    value = {}

    with pytest.raises(ValidationError) as excinfo:
        validate_schema_object(empty_swagger_spec, content_spec, value)
        unmarshal_schema_object(empty_swagger_spec, content_spec, value)
    assert excinfo.value.message == "'x' is a required property"


@pytest.mark.parametrize('nullable', [True, False])
def test_unmarshal_with_object_no_req_no_value(empty_swagger_spec, nullable):
    """When the value is not required and not set at all, validation
    should pass: (1), (7)
    """
    content_spec = content_spec_factory(False, nullable=nullable)
    value = {}

    validate_schema_object(empty_swagger_spec, content_spec, value)
    result = unmarshal_schema_object(empty_swagger_spec, content_spec, value)
    assert result == {'x': None}  # Missing parameters are re-introduced


@pytest.mark.parametrize('required', [True, False])
def test_unmarshal_with_object_no_null_value_none(empty_swagger_spec, required):
    """When nullable is `False` and the value is set to `None`, validation
    should fail: (3), (6)
    """
    content_spec = content_spec_factory(required, False)
    value = {'x': None}

    with pytest.raises(ValidationError) as excinfo:
        validate_schema_object(empty_swagger_spec, content_spec, value)
        unmarshal_schema_object(empty_swagger_spec, content_spec, value)
    assert excinfo.value.message == "None is not of type 'string'"


@pytest.mark.parametrize('required', [True, False])
def test_unmarshal_with_object_null_value_none(empty_swagger_spec, required):
    """When nullable is `True` and the value is set to `None`, validation
    should pass: (9), (12)
    """
    content_spec = content_spec_factory(required, True)
    value = {'x': None}

    validate_schema_object(empty_swagger_spec, content_spec, value)
    result = unmarshal_schema_object(empty_swagger_spec, content_spec, value)
    assert result == {'x': None}
