# -*- coding: utf-8 -*-
import json
import logging
import os.path
import warnings
from copy import deepcopy
from itertools import chain

import yaml
from jsonref import JsonRef
from jsonschema import FormatChecker
from jsonschema.validators import RefResolver
from six import iteritems
from six import iterkeys
from six.moves import range
from six.moves.urllib.parse import urlparse
from six.moves.urllib.parse import urlunparse
from six.moves.urllib.request import url2pathname
from swagger_spec_validator import validator20
from swagger_spec_validator.ref_validators import in_scope

from bravado_core import formatter
from bravado_core.exception import SwaggerSchemaError
from bravado_core.exception import SwaggerValidationError
from bravado_core.formatter import return_true_wrapper
from bravado_core.model import model_discovery
from bravado_core.resource import build_resources
from bravado_core.schema import is_dict_like
from bravado_core.schema import is_list_like
from bravado_core.schema import is_ref
from bravado_core.security_definition import SecurityDefinition
from bravado_core.spec_flattening import flattened_spec
from bravado_core.util import cached_property
from bravado_core.util import memoize_by_id
from bravado_core.util import strip_xscope


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
    'formats': [],

    # Fill with None all the missing properties during object unmarshalling
    'include_missing_properties': True,

    # What to do when a type is missing
    # If True, set the type to object and validate
    # If False, do no validation
    'default_type_to_object': False,

    # Completely dereference $refs to maximize marshaling and unmarshalling performances.
    # NOTE: this depends on validate_swagger_spec
    'internally_dereference_refs': False,

    # What value to assume for basePath if it is missing from the spec (this
    # config option is ignored if basePath is present in the spec)
    # If True, use the 'path' element of the URL the spec was retrieved from
    # If False, set basePath to '/' (conforms to Swagger 2.0 specification)
    'use_spec_url_for_base_path': False,

    # If False, use str() function for 'byte' format
    # If True, encode/decode base64 data for 'byte' format
    'use_base64_for_byte_format': False,
}


class Spec(object):
    """Represents a Swagger Specification for a service.

    :param spec_dict: Swagger API specification in json-like dict form
    :param origin_url: URL from which the spec was retrieved.
    :param http_client: Used to retrieve the spec via http/https.
    :type http_client: :class:`bravado.http_client.HTTPClient`
    :param config: Configuration dict. See CONFIG_DEFAULTS.
    """

    def __init__(
        self, spec_dict, origin_url=None, http_client=None,
        config=None,
    ):
        self.spec_dict = spec_dict
        self.origin_url = origin_url
        self.http_client = http_client
        self.api_url = None
        self.config = dict(CONFIG_DEFAULTS, **(config or {}))

        # (key, value) = (simple format def name, Model type)
        # (key, value) = (#/ format def ref, Model type)
        self.definitions = {}

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

        self.resolver = RefResolver(
            base_uri=origin_url or '',
            referrer=self.spec_dict,
            handlers=self.get_ref_handlers(),
        )

        # spec dict used to build resources, in case internally_dereference_refs config is enabled
        # it will be overridden by the dereferenced specs (by build method). More context in PR#263
        self._internal_spec_dict = spec_dict

    def __eq__(self, other):
        if id(self) == id(other):
            return True

        if not isinstance(other, self.__class__):
            return False

        # If self and other are of the same type but not pointing to the same memory location then we're going to inspect
        # all the attributes.
        for attr_name in set(
            chain(
                iterkeys(self.__dict__),
                iterkeys(other.__dict__),
            ),
        ):
            # Few attributes have recursive references to Spec or do not define an equality method we're going to ignore them
            if attr_name in {
                'definitions',  # Recursively point back to self (Spec instance). It is built via Spec.build so we're ignoring it
                'format_checker',  # jsonschema.FormatChecker does not define an equality method
                'resolver',  # jsonschema.validators.RefResolver does not define an equality method
                'resources',  # Recursively point back to self (Spec instance). It is built via Spec.build so we're ignoring it
                'security_definitions',  # Recursively point back to self (Spec instance). It is a cached property so ignore it
            }:
                continue
            try:
                if getattr(self, attr_name) != getattr(other, attr_name):
                    return False
            except AttributeError:
                return False

        return True

    def __deepcopy__(self, memo=None):
        if memo is None:
            memo = {}

        copied_self = self.__class__(spec_dict=None)
        memo[id(self)] = copied_self

        # Copy the attributes that are built via Spec.build
        for attr_name, attr_value in iteritems(self.__dict__):
            setattr(copied_self, attr_name, deepcopy(attr_value, memo=memo))

        return copied_self

    @cached_property
    def client_spec_dict(self):
        """Return a copy of spec_dict with x-scope metadata removed so that it
        is suitable for consumption by Swagger clients.

        You may be asking, "Why is there a difference between the Swagger spec
        a client sees and the one used internally?". Well, as part of the
        ingestion process, x-scope metadata is added to spec_dict so that
        $refs can be de-reffed successfully during request/response validation
        and marshalling. This metadata is specific to the context of the
        server and contains files and paths that are not relevant to the
        client. This is required so the client does not re-use (and in turn,
        re-creates) the invalid x-scope metadata created by the server.

        For example, a section of spec_dict that contains a ref would change
        as follows.

        Before:

          'MON': {
            '$ref': '#/definitions/DayHours',
            'x-scope': [
                'file:///happyhour/api_docs/swagger.json',
                'file:///happyhour/api_docs/swagger.json#/definitions/WeekHours'
            ]
          }

        After:

          'MON': {
            '$ref': '#/definitions/DayHours'
          }

        """
        return strip_xscope(self.spec_dict)

    @classmethod
    def from_dict(cls, spec_dict, origin_url=None, http_client=None, config=None):
        """Build a :class:`Spec` from Swagger API Specification

        :param spec_dict: swagger spec in json-like dict form.
        :param origin_url: the url used to retrieve the spec, if any
        :type  origin_url: str
        :param http_client: http client used to download remote $refs
        :param config: Configuration dict. See CONFIG_DEFAULTS.
        """
        spec = cls(spec_dict, origin_url, http_client, config)
        spec.build()
        return spec

    def _validate_spec(self):
        if self.config['validate_swagger_spec']:
            self.resolver = validator20.validate_spec(
                spec_dict=self.spec_dict,
                spec_url=self.origin_url or '',
                http_handlers=self.get_ref_handlers(),
            )

    def build(self):
        self._validate_spec()

        model_discovery(self)

        if self.config['internally_dereference_refs']:
            # Avoid to evaluate is_ref every time, no references are possible at this time
            self.deref = lambda ref_dict: ref_dict
            self._internal_spec_dict = self.deref_flattened_spec

        for user_defined_format in self.config['formats']:
            self.register_format(user_defined_format)

        self.resources = build_resources(self)

        self.api_url = build_api_serving_url(
            spec_dict=self.spec_dict,
            origin_url=self.origin_url,
            use_spec_url_for_base_path=self.config['use_spec_url_for_base_path'],
        )

    def get_ref_handlers(self):
        """Get mapping from URI schemes to handlers that takes a URI.

        The handlers (callables) are used by the RefResolver to retrieve
        remote specification $refs.

        :returns: dict like {'http': callable, 'https': callable}
        :rtype: dict
        """
        return build_http_handlers(self.http_client)

    def _force_deref(self, ref_dict):
        """Dereference ref_dict (if it is indeed a ref) and return what the
        ref points to.

        :param ref_dict:  {'$ref': '#/blah/blah'}
        :return: dereferenced value of ref_dict
        :rtype: scalar, list, dict
        """
        if ref_dict is None or not is_ref(ref_dict):
            return ref_dict

        # Restore attached resolution scope before resolving since the
        # resolver doesn't have a traversal history (accumulated scope_stack)
        # when asked to resolve.
        with in_scope(self.resolver, ref_dict):
            _, target = self.resolver.resolve(ref_dict['$ref'])
            return target

    # NOTE: deref gets overridden, if internally_dereference_refs is enabled, after calling build
    deref = _force_deref

    def get_op_for_request(self, http_method, path_pattern):
        """Return the Swagger operation for the passed in request http method
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
        self.format_checker.checks(name, raises=(SwaggerValidationError,))(validate)

    def get_format(self, name):
        """
        :param name: Name of the format to retrieve
        :rtype: :class:`bravado_core.formatter.SwaggerFormat`
        """
        user_defined_format = self.user_defined_formats.get(name)
        if user_defined_format is None:
            user_defined_format = formatter.DEFAULT_FORMATS.get(name)
            if name == 'byte' and self.config['use_base64_for_byte_format']:
                user_defined_format = formatter.BASE64_BYTE_FORMAT

        if user_defined_format is None:
            warnings.warn(
                message='{0} format is not registered with bravado-core!'.format(name),
                category=Warning,
            )
        return user_defined_format

    @cached_property
    def security_definitions(self):
        security_defs = {}
        for security_name, security_def in iteritems(self.spec_dict.get('securityDefinitions', {})):
            security_defs[security_name] = SecurityDefinition(self, security_def)
        return security_defs

    @cached_property
    def flattened_spec(self):
        """
        Representation of the current swagger specs that could be written to a single file.
        :rtype: dict
        """

        if not self.config['validate_swagger_spec']:
            log.warning(
                'Flattening unvalidated specs could produce invalid specs. '
                'Use it at your risk or enable `validate_swagger_specs`',
            )

        return strip_xscope(
            spec_dict=flattened_spec(swagger_spec=self),
        )

    @cached_property
    def deref_flattened_spec(self):
        deref_spec_dict = JsonRef.replace_refs(self.flattened_spec)

        @memoize_by_id
        def descend(obj):
            # Inline modification of obj
            # This method is needed because JsonRef could produce performance penalties in accessing
            # the proxied attributes
            if isinstance(obj, JsonRef):
                # Extract the proxied value
                # http://jsonref.readthedocs.io/en/latest/#jsonref.JsonRef.__subject__
                return obj.__subject__
            if is_dict_like(obj):
                for key in list(iterkeys(obj)):
                    obj[key] = descend(obj=obj[key])
            elif is_list_like(obj):
                # obj is list like object provided from flattened_spec specs.
                # This guarantees that it cannot be a tuple instance and
                # inline object modification are allowed
                for index in range(len(obj)):
                    obj[index] = descend(obj=obj[index])
            return obj

        try:
            return descend(obj=deref_spec_dict)
        finally:
            # Make sure that all memory allocated, for caching, could be released
            descend.cache.clear()


def is_yaml(url, content_type=None):
    yaml_content_types = {'application/yaml', 'application/x-yaml', 'text/yaml'}

    yaml_file_extensions = {'.yaml', '.yml'}

    if content_type in yaml_content_types:
        return True

    _, ext = os.path.splitext(url)
    if ext.lower() in yaml_file_extensions:
        return True

    return False


def build_http_handlers(http_client):
    """Create a mapping of uri schemes to callables that take a uri. The
    callable is used by jsonschema's RefResolver to download remote $refs.

    :param http_client: http_client with a request() method

    :returns: dict like {'http': callable, 'https': callable}
    """
    def download(uri):
        log.debug('Downloading %s', uri)
        request_params = {
            'method': 'GET',
            'url': uri,
        }
        response = http_client.request(request_params).result()
        content_type = response.headers.get('content-type', '').lower()
        if is_yaml(uri, content_type):
            return yaml.safe_load(response.content)
        else:
            return response.json()

    def read_file(uri):
        with open(url2pathname(urlparse(uri).path), mode='rb') as fp:
            if is_yaml(uri):
                return yaml.safe_load(fp)
            else:
                return json.loads(fp.read().decode("utf-8"))

    return {
        'http': download,
        'https': download,
        # jsonschema ordinarily handles file:// requests, but it assumes that
        # all files are json formatted. We override it here so that we can
        # load yaml files when necessary.
        'file': read_file,
    }


def build_api_serving_url(
    spec_dict, origin_url=None, preferred_scheme=None, use_spec_url_for_base_path=False,
):
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
    :param use_spec_url_for_base_path: only effective when 'basePath' is missing
        from `spec_dict`. When True, 'basePath' will be set to the path portion
        of `origin_url`. When False, 'basePath' will be set to '/'.
    :param preferred_scheme: preferred scheme to use if more than one scheme is
        supported by the API.
    :return: base url which services api requests
    :raises: SwaggerSchemaError
    """
    origin_url = origin_url or 'http://localhost/'
    origin = urlparse(origin_url)

    def pick_a_scheme(schemes):
        if not schemes:
            return origin.scheme

        if preferred_scheme:
            if preferred_scheme in schemes:
                return preferred_scheme
            raise SwaggerSchemaError(
                "Preferred scheme {0} not supported by API. Available schemes "
                "include {1}".format(preferred_scheme, schemes),
            )

        if origin.scheme in schemes:
            return origin.scheme

        return schemes[0]

    netloc = spec_dict.get('host', origin.netloc)
    base_path = '/'
    if use_spec_url_for_base_path:
        base_path = origin.path

    path = spec_dict.get('basePath', base_path)
    scheme = pick_a_scheme(spec_dict.get('schemes'))
    return urlunparse((scheme, netloc, path, None, None, None))
