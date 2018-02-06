# -*- coding: utf-8 -*-
import pytest

from bravado_core.util import AliasKeyDict
from bravado_core.util import cached_property
from bravado_core.util import determine_object_type
from bravado_core.util import memoize_by_id
from bravado_core.util import ObjectType
from bravado_core.util import sanitize_name


def test_cached_property():
    class Class(object):
        def __init__(self):
            self.calls = 0

        @cached_property
        def property_1(self):
            self.calls += 1
            return self.calls

    class_instance = Class()
    assert class_instance.calls == 0

    assert class_instance.property_1 == 1
    assert class_instance.calls == 1

    # If property is called twice no calls are received from the method
    assert class_instance.property_1 == 1
    assert class_instance.calls == 1

    # If property is deleted then the method is called again
    del class_instance.property_1
    assert class_instance.property_1 == 2
    assert class_instance.calls == 2


def test_memoize_by_id_decorator():
    calls = []

    def function(a, b=None):
        calls.append([a, b])
        return id(a) + id(b)
    decorated_function = memoize_by_id(function)

    assert decorated_function(1) == id(1) + id(None)
    assert decorated_function.cache == {
        (('a', id(1)), ('b', id(None))): id(1) + id(None)
    }
    assert calls == [[1, None]]

    assert decorated_function(2, 3) == id(2) + id(3)
    assert decorated_function.cache == {
        (('a', id(1)), ('b', id(None))): id(1) + id(None),
        (('a', id(2)), ('b', id(3))): id(2) + id(3),
    }
    assert calls == [[1, None], [2, 3]]

    # Calling the decorated method with known arguments will not call the inner method
    assert decorated_function(1) == id(1) + id(None)
    assert decorated_function.cache == {
        (('a', id(1)), ('b', id(None))): id(1) + id(None),
        (('a', id(2)), ('b', id(3))): id(2) + id(3),
    }
    assert calls == [[1, None], [2, 3]]

    decorated_function.cache.clear()

    assert decorated_function(1) == id(1) + id(None)
    assert decorated_function.cache == {
        (('a', id(1)), ('b', id(None))): id(1) + id(None)
    }
    assert calls == [[1, None], [2, 3], [1, None]]


@pytest.mark.parametrize(('input', 'expected'), [
    ('pet.getBy Id', 'pet_getBy_Id'),      # simple case
    ('_getPetById_', 'getPetById'),        # leading/trailing underscore
    ('get__Pet_By__Id', 'get_Pet_By_Id'),  # double underscores
    ('^&#@!$foo%+++:;"<>?/', 'foo'),       # bunch of illegal chars
])
def test_sanitize_name(input, expected):
    assert sanitize_name(input) == expected


def test_AliasKeyDict():
    alias_dict = AliasKeyDict({'a': 'b', 'c': 'd'})
    alias_dict.add_alias('alias_a', 'a')
    assert len(alias_dict) == 2
    assert set(alias_dict.items()) == set([('a', 'b'), ('c', 'd')])
    assert 'alias_a' in alias_dict
    assert alias_dict['alias_a'] is alias_dict['a']
    assert alias_dict.get('alias_a') is alias_dict.get('a')
    assert alias_dict.get('f', 'not there') == 'not there'

    assert alias_dict.pop('alias_a') == 'b'
    assert len(alias_dict) == 1
    assert 'a' not in alias_dict
    assert 'alias_a' not in alias_dict


def test_AliasKeyDict_copy():
    alias_dict = AliasKeyDict([('foo', 'bar')])
    alias_dict.add_alias('baz', 'foo')
    dict_copy = alias_dict.copy()
    assert set(dict_copy.items()) == set(alias_dict.items())
    assert dict_copy.alias_to_key == alias_dict.alias_to_key


def test_AliasKeyDict_del():
    alias_dict = AliasKeyDict([('foo', 'bar')])
    alias_dict.add_alias('baz', 'foo')
    del alias_dict['baz']
    assert len(alias_dict) == 0
    assert 'baz' not in alias_dict
    assert 'foo' not in alias_dict


@pytest.mark.parametrize(
    'object_dict, expected_object_type',
    (
        [{'in': 'body', 'name': 'body', 'required': True, 'schema': {'type': 'object'}}, ObjectType.PARAMETER],
        [{'get': {'responses': {'200': {'description': 'response description'}}}}, ObjectType.PATH_ITEM],
        [{'description': 'response description', 'schema': {'type': 'object'}}, ObjectType.RESPONSE],
        [{'description': 'response description', 'parameters': {'param': {'type': 'object'}}}, ObjectType.SCHEMA],
    )
)
def test_determine_object_type(object_dict, expected_object_type):
    assert determine_object_type(object_dict) == expected_object_type
