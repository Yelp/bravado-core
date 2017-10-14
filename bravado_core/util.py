# -*- coding: utf-8 -*-
import inspect
from functools import wraps

from six import iteritems


class cached_property(object):
    """
    A property that is only computed once per instance and then replaces
    itself with an ordinary attribute. Deleting the attribute resets the
    property.

    Source: https://github.com/bottlepy/bottle/commit/fa7733e075da0d790d809aa3d2f53071897e6f76
    """

    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


def memoize_by_id(func):
    cache = func.cache = {}
    _CACHE_MISS = object()

    def make_key(*args, **kwargs):
        return tuple((key, id(value)) for key, value in sorted(iteritems(inspect.getcallargs(func, *args, **kwargs))))

    @wraps(func)
    def wrapper(*args, **kwargs):
        cache_key = make_key(*args, **kwargs)
        cached_value = cache.get(cache_key, _CACHE_MISS)
        if cached_value is _CACHE_MISS:
            cached_value = func(*args, **kwargs)
            cache[cache_key] = cached_value
        return cached_value
    return wrapper
