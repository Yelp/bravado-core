# -*- coding: utf-8 -*-
import logging

import jsonref
from six import iteritems
from six.moves.urllib import parse as urlparse
from swagger_spec_validator import validator20
from bravado_core.exception import SwaggerSchemaError

from bravado_core.model import build_models
from bravado_core.model import tag_models
from bravado_core.model import fix_malformed_model_refs
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
    'use_models': True
}


class Spec(object):
    """Represents a Swagger Specification for a service.
    """

    def __init__(self, spec_dict, origin_url=None, http_client=None,
                 config=None):
        """
        :param spec_dict: Swagger API specification in json-like dict form
        :param origin_url: URL from which the spec was retrieved.
        :param http_client: :class:`bravado_core.http_client.HTTPClient`
        :param config: Configuration dict. See CONFIG_DEFAULTS.
        """
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
        tag_models(spec_dict)
        fix_malformed_model_refs(spec_dict)
        spec_dict = jsonref.JsonRef.replace_refs(spec_dict,
                                                 base_uri=origin_url or '')
        replace_jsonref_proxies(spec_dict)
        spec = cls(spec_dict, origin_url, http_client, config)
        spec.build()
        return spec

    def build(self):
        if self.config['validate_swagger_spec']:
            validator20.validate_spec(self.spec_dict)

        self.api_url = build_api_serving_url(self.spec_dict, self.origin_url)
        self.definitions = build_models(self.spec_dict.get('definitions', {}))
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


def replace_jsonref_proxies(obj):
    """
    Replace jsonref proxies in the given json obj with the proxy target.
    Updates are made in place. This removes compatibility problems with 3rd
    party libraries that can't handle jsonref proxy objects.

    :param obj: json like object
    :type obj: int, bool, string, float, list, dict, etc
    """
    # TODO: consider upstreaming in the jsonref library as a util method
    def descend(fragment):
        if is_dict_like(fragment):
            for k, v in iteritems(fragment):
                if isinstance(v, jsonref.JsonRef):
                    fragment[k] = v.__subject__
                descend(fragment[k])
        elif is_list_like(fragment):
            for index, element in enumerate(fragment):
                if isinstance(element, jsonref.JsonRef):
                    fragment[index] = element.__subject__
                descend(element)

    descend(obj)
