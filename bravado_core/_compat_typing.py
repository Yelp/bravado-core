# -*- coding: utf-8 -*-
import typing
from mypy_extensions import Arg
from typing import NoReturn  # NOTE: This is available on Python3.5.4+  # noqa: F401
JSONDict = typing.Dict[typing.Text, typing.Any]
UnmarshalingMethod = typing.Callable[[Arg(typing.Any, 'value')], typing.Any]
Func = typing.Callable[..., typing.Any]
FuncType = typing.TypeVar('FuncType', bound=Func)
