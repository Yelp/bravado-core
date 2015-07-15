import sys

import six


class SwaggerError(Exception):
    """Base exception class which all bravado-core specific exceptions
    inherit from.
    """
    pass


class SwaggerMappingError(SwaggerError):
    """Raised when an error is encountered during processing of a request or
    a response.
    """

    def __init__(self, msg, cause=None):
        """
        :param msg: String message for the error.
        :param cause: Optional exception that caused this one.
        """
        super(Exception, self).__init__(msg, cause)


class SwaggerSchemaError(SwaggerError):
    """Raised when an error is encountered during processing of a SwaggerSchema.
    """
    pass


def wrap_exception(exception_class):
    def generic_exception(method):
        def wrapper(*args, **kwargs):
            try:
                method(*args, **kwargs)
            except Exception as e:
                six.reraise(
                    exception_class,
                    exception_class(str(e)),
                    sys.exc_info()[2])
        return wrapper
    return generic_exception
