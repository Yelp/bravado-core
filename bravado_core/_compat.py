# -*- coding: utf-8 -*-
import six

if six.PY2:  # pragma: no cover  # py2
    from functools32 import wraps  # noqa: F401
else:  # pragma: no cover  # py3+
    from functools import wraps  # noqa: F401
