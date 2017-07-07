# -*- coding: utf-8 -*-
from bravado_core.spec import strip_xscope


def test_empty():
    assert {} == strip_xscope({})


def test_contained_in_dict():
    fragment = {
        'MON': {
            '$ref': '#/definitions/DayHours',
            'x-scope': [
                'file:///happyhour/api_docs/swagger.json',
                'file:///happyhour/api_docs/swagger.json#/definitions/WeekHours'
            ]
        }
    }
    expected = {
        'MON': {
            '$ref': '#/definitions/DayHours',
        }
    }
    assert expected == strip_xscope(fragment)
    assert 'x-scope' in fragment['MON']


def test_contained_in_list():
    fragment = [
        {
            '$ref': '#/definitions/DayHours',
            'x-scope': [
                'file:///happyhour/api_docs/swagger.json',
                'file:///happyhour/api_docs/swagger.json#/definitions/WeekHours'
            ]
        }
    ]
    expected = [
        {
            '$ref': '#/definitions/DayHours',
        }
    ]
    assert expected == strip_xscope(fragment)
    assert 'x-scope' in fragment[0]


def test_no_op():
    fragment = {
        'MON': {
            '$ref': '#/definitions/DayHours',
        }
    }
    expected = {
        'MON': {
            '$ref': '#/definitions/DayHours',
        }
    }
    assert expected == strip_xscope(fragment)


def test_petstore_spec(petstore_spec):
    assert petstore_spec.client_spec_dict == strip_xscope(petstore_spec.spec_dict)
