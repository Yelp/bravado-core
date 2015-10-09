# -*- coding: utf-8 -*-
import functools
import logging
import warnings

import jsonref
from jsonschema import FormatChecker
from six.moves.urllib import parse as urlparse
from swagger_spec_validator import validator20

from bravado_core import formatter
from bravado_core.exception import SwaggerSchemaError, SwaggerValidationError
from bravado_core.formatter import return_true_wrapper
from bravado_core.model import annotate_with_xmodel_callback
from bravado_core.model import create_dereffed_models_callback
from bravado_core.model import create_reffed_models_callback
from bravado_core.model import fix_malformed_model_refs
from bravado_core.model import fix_models_with_no_type_callback
from bravado_core.resource import build_resources
from bravado_core.schema import is_dict_like, is_list_like


log = logging.getLogger(__name__)


CONFIG_DEFAULTS = {
    # On the client side, validate incoming responses
    # On the server side, validate outgoing responses
    'validate_responses': True,

    # On the client side, validate outgoing requests
    # On the server side, validate incoming requests
    'validate_requests': True,

    # Use swagger_spec_validator to validate the swagger spec
    'validate_swagger_spec': True,

    # Use Python classes (models) instead of dicts for #/definitions/{models}
    # On the client side, this applies to incoming responses.
    # On the server side, this applies to incoming requests.
    #
    # NOTE: outgoing requests on the client side and outgoing responses on the
    #       server side can use either models or dicts.
    'use_models': True,

    # List of user-defined formats of type
    # :class:`bravado_core.formatter.SwaggerFormat`. These formats are in
    # addition to the formats already supported by the Swagger 2.0
    # Specification.
    'formats': []
}


class Spec(object):
    """Represents a Swagger Specification for a service.

    :param spec_dict: Swagger API specification in json-like dict form
    :param origin_url: URL from which the spec was retrieved.
    :param http_client: Used to retrive the spec via http/https.
    :type http_client: :class:`bravado.http_client.HTTPClient`
    :param config: Configuration dict. See CONFIG_DEFAULTS.
    """
    def __init__(self, spec_dict, origin_url=None, http_client=None,
                 config=None):
        self.spec_dict = spec_dict
        self.origin_url = origin_url
        self.http_client = http_client
        self.api_url = None
        self.config = dict(CONFIG_DEFAULTS, **(config or {}))

        # (key, value) = (simple format def name, Model type)
        # (key, value) = (#/ format def ref, Model type)
        self.definitions = None

        # (key, value) = (simple resource name, Resource)
        # (key, value) = (#/ format resource ref, Resource)
        self.resources = None

        # (key, value) = (simple ref name, param_spec in dict form)
        # (key, value) = (#/ format ref name, param_spec in dict form)
        self.params = None

        # Built on-demand - see get_op_for_request(..)
        self._request_to_op_map = None

        # (key, value) = (format name, SwaggerFormat)
        self.user_defined_formats = {}
        self.format_checker = FormatChecker()

    @classmethod
    def from_dict(cls, spec_dict, origin_url=None, http_client=None,
                  config=None):
        """
        Build a :class:`Spec` from Swagger API Specificiation

        :param spec_dict: swagger spec in json-like dict form.
        :param origin_url: the url used to retrieve the spec, if any
        :type  origin_url: str
        :param config: Configuration dict. See CONFIG_DEFAULTS.
        """
        fix_malformed_model_refs(spec_dict)
        spec_dict = jsonref.JsonRef.replace_refs(
            spec_dict, base_uri=origin_url or '')

        # Populated by post-processing callbacks below
        models = {}

        post_process_spec(
            spec_dict,
            on_container_callbacks=(
                annotate_with_xmodel_callback,
                fix_models_with_no_type_callback,
                functools.partial(create_reffed_models_callback, models),
                functools.partial(create_dereffed_models_callback, models),
                replace_jsonref_proxies_callback,
            ))

        spec = cls(spec_dict, origin_url, http_client, config)
        spec.definitions = models
        spec.build()
        return spec

    def build(self):
        for format in self.config['formats']:
            self.register_format(format)

        if self.config['validate_swagger_spec']:
            validator20.validate_spec(self.spec_dict)

        self.api_url = build_api_serving_url(self.spec_dict, self.origin_url)
        self.resources = build_resources(self)

    def get_op_for_request(self, http_method, path_pattern):
        """
        Return the Swagger operation for the passed in request http method
        and path pattern. Makes it really easy for server-side implementations
        to map incoming requests to the Swagger spec.

        :param http_method: http method of the request
        :param path_pattern: request path pattern. e.g. /foo/{bar}/baz/{id}
        :returns: the matching operation or None if a match couldn't be found
        :rtype: :class:`bravado_core.operation.Operation`
        """
        if self._request_to_op_map is None:
            # lazy initialization
            self._request_to_op_map = {}
            base_path = self.spec_dict.get('basePath', '').rstrip('/')
            for resource in self.resources.values():
                for op in resource.operations.values():
                    full_path = base_path + op.path_name
                    key = (op.http_method, full_path)
                    self._request_to_op_map[key] = op

        key = (http_method.lower(), path_pattern)
        return self._request_to_op_map.get(key)

    def register_format(self, user_defined_format):
        """Registers a user-defined format to be used with this spec.

        :type user_defined_format:
            :class:`bravado_core.formatter.SwaggerFormat`
        """
        name = user_defined_format.format
        self.user_defined_formats[name] = user_defined_format
        validate = return_true_wrapper(user_defined_format.validate)
        self.format_checker.checks(
            name, raises=(SwaggerValidationError,))(validate)

    def get_format(self, name):
        """
        :param name: Name of the format to retrieve
        :rtype: :class:`bravado_core.formatters.SwaggerFormat`
        """
        if name in formatter.DEFAULT_FORMATS:
            return formatter.DEFAULT_FORMATS[name]
        format = self.user_defined_formats.get(name)
        if format is None:
            warnings.warn('{0} format is not registered with bravado-core!'
                          .format(name), Warning)
        return format


def build_api_serving_url(spec_dict, origin_url=None, preferred_scheme=None):
    """The URL used to service API requests does not necessarily have to be the
    same URL that was used to retrieve the API spec_dict.

    The existence of three fields in the root of the specification govern
    the value of the api_serving_url:

    - host string
        The host (name or ip) serving the API. This MUST be the host only and
        does not include the scheme nor sub-paths. It MAY include a port.
        If the host is not included, the host serving the documentation is to
        be used (including the port). The host does not support path templating.

    - basePath string
        The base path on which the API is served, which is relative to the
        host. If it is not included, the API is served directly under the host.
        The value MUST start with a leading slash (/). The basePath does not
        support path templating.

    - schemes [string]
        The transfer protocol of the API. Values MUST be from the list:
        "http", "https", "ws", "wss". If the schemes is not included,
        the default scheme to be used is the one used to access the
        specification.

    See https://github.com/swagger-api/swagger-spec_dict/blob/master/versions/2.0.md#swagger-object-   # noqa

    :param spec_dict: the Swagger spec in json-like dict form
    :param origin_url: the URL from which the spec was retrieved, if any. This
        is only used in Swagger clients.
    :param preferred_scheme: preferred scheme to use if more than one scheme is
        supported by the API.
    :return: base url which services api requests
    :raises: SwaggerSchemaError
    """
    origin_url = origin_url or 'http://localhost/'
    origin = urlparse.urlparse(origin_url)

    def pick_a_scheme(schemes):
        if not schemes:
            return origin.scheme

        if preferred_scheme:
            if preferred_scheme in schemes:
                return preferred_scheme
            raise SwaggerSchemaError(
                "Preferred scheme {0} not supported by API. Available schemes "
                "include {1}".format(preferred_scheme, schemes))

        if origin.scheme in schemes:
            return origin.scheme

        if len(schemes) == 1:
            return schemes[0]

        raise SwaggerSchemaError(
            "Origin scheme {0} not supported by API. Available schemes "
            "include {1}".format(origin.scheme, schemes))

    netloc = spec_dict.get('host', origin.netloc)
    path = spec_dict.get('basePath', origin.path)
    scheme = pick_a_scheme(spec_dict.get('schemes'))
    return urlparse.urlunparse((scheme, netloc, path, None, None, None))


def post_process_spec(spec_dict, on_container_callbacks):
    """Post-process the passed in spec_dict.

    For each container type (list or dict) that is traversed in spec_dict,
    the list of passed in callbacks is called with arguments (container, key).

    When the container is a dict, key is obviously the key for the value being
    traversed.

    When the container is a list, key is an integer index into the list of the
    value being traversed.

    :param spec_dict: Swagger spec in dict form
    :param on_container_callbacks: list of callbacks to be invoked on each
        container type.
    """
    def fire_callbacks(container, key):
        for callback in on_container_callbacks:
            callback(container, key)

    def descend(fragment):
        if is_dict_like(fragment):
            for key in fragment:
                fire_callbacks(fragment, key)
                descend(fragment[key])
        elif is_list_like(fragment):
            for index in range(len(fragment)):
                fire_callbacks(fragment, index)
                descend(fragment[index])

    descend(spec_dict)


def replace_jsonref_proxies_callback(container, key):
    """Replace jsonref proxies in the given dict or list with the proxy target.
    Updates are made in place. This removes compatibility problems with 3rd
    party libraries that can't handle jsonref proxy objects while traversing
    the swagger spec dict.

    :type container: list or dict
    :type key: string when the container is a dict, integer when the container
        is a list
    """
    jsonref_proxy = container[key]
    if isinstance(jsonref_proxy, jsonref.JsonRef):
        container[key] = jsonref_proxy.__subject__
