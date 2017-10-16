# -*- coding: utf-8 -*-
from bravado_core.util import cached_property


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
