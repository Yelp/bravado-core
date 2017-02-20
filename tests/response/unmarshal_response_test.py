from mock import Mock, patch

import pytest

from bravado_core.response import IncomingResponse, unmarshal_response


@pytest.fixture
def response_spec():
    return {
        'description': "Day of the week",
        'schema': {
            'type': 'string',
        }
    }


def test_no_content(empty_swagger_spec):
    response_spec = {
        'description': "I don't have a 'schema' key so I return nothing",
    }
    response = Mock(spec=IncomingResponse, status_code=200)

    with patch('bravado_core.response.get_response_spec') as m:
        m.return_value = response_spec
        op = Mock(swagger_spec=empty_swagger_spec)
        result = unmarshal_response(response, op)
        assert result is None

def test_invalid_json_content(empty_swagger_spec, response_spec):
    response = Mock(
        spec=IncomingResponse,
        status_code=200,
        json=Mock(side_effect=ValueError()),
        text='blah',
    )

    with patch('bravado_core.response.get_response_spec') as m:
        with pytest.raises(ValueError):
            m.return_value = response_spec
            op = Mock(swagger_spec=empty_swagger_spec)
            unmarshal_response(response, op)


def test_json_content(empty_swagger_spec, response_spec):
    response = Mock(
        spec=IncomingResponse,
        status_code=200,
        json=Mock(return_value='Monday'))

    with patch('bravado_core.response.get_response_spec') as m:
        m.return_value = response_spec
        op = Mock(swagger_spec=empty_swagger_spec)
        assert 'Monday' == unmarshal_response(response, op)


def test_skips_validation(empty_swagger_spec, response_spec):
    empty_swagger_spec.config['validate_responses'] = False
    response = Mock(
        spec=IncomingResponse,
        status_code=200,
        json=Mock(return_value='Monday'))

    with patch('bravado_core.response.validate_schema_object') as val_schem:
        with patch('bravado_core.response.get_response_spec') as get_resp:
            get_resp.return_value = response_spec
            op = Mock(swagger_spec=empty_swagger_spec)
            unmarshal_response(response, op)
            assert val_schem.call_count == 0


def test_performs_validation(empty_swagger_spec, response_spec):
    empty_swagger_spec.config['validate_responses'] = True
    response = Mock(
        spec=IncomingResponse,
        status_code=200,
        json=Mock(return_value='Monday'))

    with patch('bravado_core.response.validate_schema_object') as val_schem:
        with patch('bravado_core.response.get_response_spec') as get_resp:
            get_resp.return_value = response_spec
            op = Mock(swagger_spec=empty_swagger_spec)
            unmarshal_response(response, op)
            assert val_schem.call_count == 1
