# -*- coding: utf-8 -*-
import inspect
import re
from functools import wraps

from six import iteritems


SANITIZE_RULES = [
    (re.compile(regex), replacement)
    for regex, replacement in [
        ('[^A-Za-z0-9_]', '_'),  # valid chars for method names
        ('__+', '_'),  # collapse consecutive _
        ('^[0-9_]|_$', ''),  # trim leading/trailing _ and leading digits
    ]
]


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


def sanitize_name(name):
    """Convert a given name so that it is a valid python identifier."""
    for regex, replacement in SANITIZE_RULES:
        name = regex.sub(replacement, name)

    return name


class AliasKeyDict(dict):
    """Dictionary class that allows you to set additional key names for existing keys. Retrieving
    values using these aliased keys works, but when iterating over the dictionary, only the main
    keys are returned."""

    def __init__(self, *args, **kwargs):
        super(AliasKeyDict, self).__init__(*args, **kwargs)
        self.alias_to_key = {}

    def add_alias(self, alias, key):
        if alias != key:
            self.alias_to_key[alias] = key

    def determine_key(self, key):
        if key in self.alias_to_key:  # this will normally be False, optimize for it
            key = self.alias_to_key[key]
        return key

    def get(self, key, *args, **kwargs):
        return super(AliasKeyDict, self).get(self.determine_key(key), *args, **kwargs)

    def pop(self, key, *args, **kwargs):
        return super(AliasKeyDict, self).pop(self.determine_key(key), *args, **kwargs)

    def __getitem__(self, key):
        return super(AliasKeyDict, self).__getitem__(self.determine_key(key))

    def __delitem__(self, key):
        final_key = self.alias_to_key.get(key, key)
        if final_key != key:
            del self.alias_to_key[key]
        return super(AliasKeyDict, self).__delitem__(final_key)

    def __contains__(self, key):
        return super(AliasKeyDict, self).__contains__(self.determine_key(key))

    def copy(self):
        copied_dict = type(self)(self)
        copied_dict.alias_to_key = self.alias_to_key.copy()
        return copied_dict
