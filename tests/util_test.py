# -*- coding: utf-8 -*-
from bravado_core.util import cached_property
from bravado_core.util import memoize_by_id


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
