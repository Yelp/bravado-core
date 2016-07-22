import pytest

from bravado_core.unmarshal import unmarshal_schema_object
from bravado_core.validate import validate_schema_object
from jsonschema.exceptions import ValidationError


@pytest.mark.parametrize('value', ['x', None])
@pytest.mark.parametrize('nullable', [True, False])
def test_unmarshal_with_primitive(empty_swagger_spec, value, nullable):
    """If the value is a primitive, validation should pass if
    `x-nullable` is `True` and the value is `None`. `required` is not
    possible in this scenario.

    +---------------------+--------------+
    | x-nullable == False | 'x'  -> pass |
    |                     | None -> fail |
    +---------------------+--------------+
    | x-nullable == True  | 'x'  -> pass |
    |                     | None -> pass |
    +---------------------+--------------+
    """
    content_spec = {
        'type': 'string',
        'x-nullable': nullable,
    }

    try:
        validate_schema_object(empty_swagger_spec, content_spec, value)
        result = unmarshal_schema_object(
            empty_swagger_spec, content_spec, value)
    except ValidationError as e:
        result = e

    if nullable is False and not value:
        assert result.message == "None is not of type 'string'"
    else:
        assert result == value


@pytest.mark.parametrize('value', [{'x': 'y'}, {'x': None}, {}])
@pytest.mark.parametrize('nullable', [True, False])
@pytest.mark.parametrize('required', [True, False])
def test_unmarshal_with_object(empty_swagger_spec, value, nullable, required):
    """If the value is an object, validation should pass if
    `x-nullable` is `True` and the value is `None`. `required` doesn't
    have an influence.

    +---------------------+---------------------+---------------------+
    |                     | required == False   | required == True    |
    +---------------------+---------------------+---------------------+
    | x-nullable == False | {}          -> pass | {}          -> fail |
    |                     | {'x': 'y'}  -> pass | {'x': 'y'}  -> pass |
    |                     | {'x': None} -> fail | {'x': None} -> fail |
    +---------------------+---------------------+---------------------+
    | x-nullable == True  | {}          -> pass | {}          -> fail |
    |                     | {'x': 'y'}  -> pass | {'x': 'y'}  -> pass |
    |                     | {'x': None} -> pass | {'x': None} -> pass |
    +---------------------+---------------------+---------------------+
    """
    content_spec = {
        'type': 'object',
        'required': ['x'] if required else [],
        'properties': {
            'x': {
                'type': 'string',
                'x-nullable': nullable,
            }
        }
    }

    try:
        validate_schema_object(empty_swagger_spec, content_spec, value)
        result = unmarshal_schema_object(
            empty_swagger_spec, content_spec, value)
    except ValidationError as e:
        result = e

    if value == {} and required is True:
        assert result.message == "'x' is a required property"
    elif value == {} and required is False:
        # Unmarshal re-introduces missing properties with None which is ok.
        assert result == {'x': None}
    elif nullable is False and value['x'] is None:
        assert result.message == "None is not of type 'string'"
    else:
        result == value
