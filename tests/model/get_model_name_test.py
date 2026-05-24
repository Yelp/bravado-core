# -*- coding: utf-8 -*-
try:
    from unittest import mock
except ImportError:
    import mock
import pytest

from bravado_core.model import _get_model_name


@pytest.mark.parametrize(
    'model_dict, expected_name',
    (
        ({}, None),
        ({'x-model': mock.sentinel.MODEL_MARKER}, mock.sentinel.MODEL_MARKER),
        ({'title': mock.sentinel.TITLE}, mock.sentinel.TITLE),
        ({'x-model': mock.sentinel.MODEL_MARKER, 'title': mock.sentinel.TITLE}, mock.sentinel.MODEL_MARKER),
    ),
)
def test__get_model_name(model_dict, expected_name):
    assert _get_model_name(model_dict) == expected_name
