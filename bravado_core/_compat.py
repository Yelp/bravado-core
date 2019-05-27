# -*- coding: utf-8 -*-
import six


if six.PY2:  # pragma: no cover  # py2
    from functools32 import wraps  # noqa: F401
else:  # pragma: no cover  # py3+
    from functools import wraps  # noqa: F401


try:
    from collections.abc import Mapping  # noqa: F401  # pragma: no cover  # py3.3+
except ImportError:
    from collections import Mapping  # noqa: F401  # py3.2 or older
