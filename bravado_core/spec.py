# -*- coding: utf-8 -*-
import copy
import functools
import json
import logging
import os.path
import warnings
from contextlib import closing

import yaml
from jsonref import JsonRef
from jsonschema import FormatChecker
from jsonschema.compat import urlopen
from jsonschema.validators import RefResolver
from six import iteritems
from six import iterkeys
from six.moves import range
from six.moves.urllib.parse import urlparse
from six.moves.urllib.parse import urlunparse
from swagger_spec_validator import validator20
from swagger_spec_validator.ref_validators import attach_scope
from swagger_spec_validator.ref_validators import in_scope

from bravado_core import formatter
from bravado_core.exception import SwaggerSchemaError
from bravado_core.exception import SwaggerValidationError
from bravado_core.formatter import return_true_wrapper
from bravado_core.model import collect_models
from bravado_core.model import tag_models
from bravado_core.resource import build_resources
from bravado_core.schema import is_dict_like
from bravado_core.schema import is_list_like
from bravado_core.schema import is_ref
from bravado_core.security_definition import SecurityDefinition
from bravado_core.spec_flattening import flattened_spec
from bravado_core.util import cached_property
from bravado_core.util import memoize_by_id


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

    # Fill with None all the missing properties during object unmarshal-ing
    'include_missing_properties': True,

    # What to do when a type is missing
    # If True, set the type to object and validate
    # If False, do no validation
    'default_type_to_object': False,

    # Completely dereference $refs to maximize marshaling and unmarshaling performances.
    # NOTE: this depends on validate_swagger_spec
    'internally_dereference_refs': False,
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
            handlers=build_http_handlers(http_client),
        )

        self._validate_config()

        if self.config['internally_dereference_refs']:
            # If internally_dereference_refs is enabled we do NOT need to resolve references anymore
            # it's useless to evaluate is_ref every time
            self.deref = lambda ref_dict: ref_dict
        else:
            self.deref = self._force_deref

    def _validate_config(self):
        """
        Validates the correctness of the configurations injected and makes sure that:
        - no extra config keys are available on the config dictionary
        - dependent configs are checked

        :return: True if the initial configs are valid, False otherwise
        :rtype: bool
        """
        are_config_changed = False

        extraneous_keys = set(iterkeys(self.config)) - set(iterkeys(CONFIG_DEFAULTS))
        if extraneous_keys:
            are_config_changed = True
            for key in extraneous_keys:
                warnings.warn(
                    message='config {} is not a recognized config key'.format(key),
                    category=Warning,
                )

        if self.config['internally_dereference_refs'] and not self.config['validate_swagger_spec']:
            are_config_changed = True
            self.config['internally_dereference_refs'] = False
            warnings.warn(
                message='internally_dereference_refs config disabled because validate_swagger_spec has to be enabled',
                category=Warning,
            )

        return not are_config_changed

    @cached_property
    def client_spec_dict(self):
        """Return a copy of spec_dict with x-scope metadata removed so that it
        is suitable for consumption by Swagger clients.

        You may be asking, "Why is there a difference between the Swagger spec
        a client sees and the one used internally?". Well, as part of the
        ingestion process, x-scope metadata is added to spec_dict so that
        $refs can be de-reffed successfully during requset/response validation
        and marshalling. This medatadata is specific to the context of the
        server and contains files and paths that are not relevant to the
        client. This is required so the client does not re-use (and in turn,
        re-creates) the invalid x-scope metadata created by the server.

        For example, a section of spec_dict that contains a ref would change
        as folows.

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
        """Build a :class:`Spec` from Swagger API Specificiation

        :param spec_dict: swagger spec in json-like dict form.
        :param origin_url: the url used to retrieve the spec, if any
        :type  origin_url: str
        :param: http_client: http client used to download remote $refs
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
                http_handlers=build_http_handlers(self.http_client),
            )

    def build(self):
        self._validate_spec()
        post_process_spec(
            self,
            on_container_callbacks=[
                functools.partial(
                    tag_models,
                    visited_models={},
                    swagger_spec=self,
                ),
                functools.partial(
                    collect_models,
                    models=self.definitions,
                    swagger_spec=self,
                ),
            ],
        )

        for format in self.config['formats']:
            self.register_format(format)

        self.api_url = build_api_serving_url(self.spec_dict, self.origin_url)
        self.resources = build_resources(self)

    @cached_property
    def _internal_spec_dict(self):
        if self.config['internally_dereference_refs']:
            return self.deref_flattened_spec
        else:
            return self.spec_dict

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

    def deref(self, ref_dict):
        # This method is actually set in __init__
        pass

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
        self.format_checker.checks(
            name, raises=(SwaggerValidationError,))(validate)

    def get_format(self, name):
        """
        :param name: Name of the format to retrieve
        :rtype: :class:`bravado_core.formatters.SwaggerFormat`
        """
        format = self.user_defined_formats.get(name)
        if format is None:
            format = formatter.DEFAULT_FORMATS.get(name)

        if format is None:
            warnings.warn(
                message='{0} format is not registered with bravado-core!'.format(name),
                category=Warning,
            )
        return format

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
        NOTE: The representation strips out all the definitions that are not referenced
        :return:
        """

        if not self.config['validate_swagger_spec']:
            raise RuntimeError('Swagger Specs have to be validated before flattening.')

        # If resources are defined it means that Spec has been built and so swagger specs have been validated
        if self.resources is None:
            self._validate_spec()

        return strip_xscope(
            spec_dict=flattened_spec(
                spec_dict=self.spec_dict,
                spec_resolver=self.resolver,
                spec_url=self.origin_url,
                http_handlers=build_http_handlers(self.http_client),
                spec_definitions=self.definitions,
            ),
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
                    obj[key] = descend(obj[key])
            elif is_list_like(obj):
                # obj is list like object provided from flattened_spec specs.
                # This guarantees that it cannot be a tuple instance and
                # inline object modification are allowed
                for index in range(len(obj)):
                    obj[index] = descend(obj[index])
            return obj

        try:
            return descend(deref_spec_dict)
        finally:
            # Make sure that all memory allocated, for caching, could be released
            descend.cache.clear()


def is_yaml(url, content_type=None):
    yaml_content_types = set([
        'application/yaml',
        'application/x-yaml',
        'text/yaml',
    ])

    yaml_file_extensions = set(['.yaml', '.yml'])

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

    :returns: dict like {'http': callable, 'https': callable)
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
        with closing(urlopen(uri)) as fp:
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
    origin = urlparse(origin_url)

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
    return urlunparse((scheme, netloc, path, None, None, None))


def post_process_spec(swagger_spec, on_container_callbacks):
    """Post-process the passed in swagger_spec.spec_dict.

    For each container type (list or dict) that is traversed in spec_dict,
    the list of passed in callbacks is called with arguments (container, key).

    When the container is a dict, key is obviously the key for the value being
    traversed.

    When the container is a list, key is an integer index into the list of the
    value being traversed.

    In addition to firing the passed in callbacks, $refs are annotated with
    an 'x-scope' key that contains the current _scope_stack of the RefResolver.
    The 'x-scope' _scope_stack is used during request/response marshalling to
    assume a given scope before de-reffing $refs (otherwise, de-reffing won't
    work).

    :type swagger_spec: :class:`bravado_core.spec.Spec`
    :param on_container_callbacks: list of callbacks to be invoked on each
        container type.
    """
    def fire_callbacks(container, key, path):
        for callback in on_container_callbacks:
            callback(container, key, path)

    resolver = swagger_spec.resolver

    def skip_already_visited_fragments(func):
        func.cache = cache = set()

        @functools.wraps(func)
        def wrapper(fragment, *args, **kwargs):
            is_reference = is_ref(fragment)
            if is_reference:
                ref = fragment['$ref']
                attach_scope(fragment, resolver)
                with resolver.resolving(ref) as target:
                    if id(target) in cache:
                        log.debug('Already visited %s', ref)
                        return

                    func(target, *args, **kwargs)
                    return

            # fragment is guaranteed not to be a ref from this point onwards
            fragment_id = id(fragment)

            if fragment_id in cache:
                log.debug('Already visited id %d', fragment_id)
                return

            cache.add(id(fragment))
            func(fragment, *args, **kwargs)
        return wrapper

    @skip_already_visited_fragments
    def descend(fragment, path=None, visited_refs=None):
        """
        :param fragment: node in spec_dict
        :param path: list of strings that form the current path to fragment
        :param visited_refs: list of visted ref_dict
        """
        path = path or []
        visited_refs = visited_refs or []

        if is_dict_like(fragment):
            for key, value in iteritems(fragment):
                fire_callbacks(fragment, key, path + [key])
                descend(fragment[key], path + [key], visited_refs)

        elif is_list_like(fragment):
            for index in range(len(fragment)):
                fire_callbacks(fragment, index, path + [str(index)])
                descend(fragment[index], path + [str(index)], visited_refs)

    try:
        descend(swagger_spec.spec_dict)
    finally:
        descend.cache.clear()

    if swagger_spec.config['internally_dereference_refs']:
        # While building models we need to rebuild them by using fully dereference specs in order
        # to get proper validation of polymorphic objects
        # NOTE: It cannot be a replacement of ``descend(swagger_spec.spec_dict)`` because
        # swagger_specs.deref_flattened_spec needs already built models in order to add not used
        # models in the discovered models/definitions
        try:
            descend(swagger_spec.deref_flattened_spec)
        finally:
            # Make sure that all memory allocated, for caching, could be released
            descend.cache.clear()


def strip_xscope(spec_dict):
    """
    :param spec_dict: Swagger spec in dict form. This is treated as read-only.
    :return: deep copy of spec_dict with the x-scope metadata stripped out.
    """
    result = copy.deepcopy(spec_dict)

    def descend(fragment):
        if is_dict_like(fragment):
            for key in list(fragment.keys()):
                if key == 'x-scope':
                    del fragment['x-scope']
                else:
                    descend(fragment[key])
        elif is_list_like(fragment):
            for element in fragment:
                descend(element)

    descend(result)
    return result
