# -*- coding: utf-8 -*-
import logging

from six import iteritems

from bravado_core.exception import SwaggerSchemaError
from bravado_core.param import Param
from bravado_core.security_requirement import SecurityRequirement
from bravado_core.util import AliasKeyDict
from bravado_core.util import cached_property
from bravado_core.util import sanitize_name

log = logging.getLogger(__name__)


def _sanitize_operation_id(operation_id, http_method, path_name):
    sanitized_operation_id = sanitize_name(operation_id or '')

    # Handle crazy corner cases where someone explictily sets operation
    # id a value that gets sanitized down to an empty string
    if len(sanitized_operation_id) == 0:
        # build based on the http method and request path
        sanitized_operation_id = sanitize_name(http_method + '_' + path_name)

    # Handle super crazy corner case where even ``http_method + '_' + path_name``
    # gets sanitized down to an empty string
    if len(sanitized_operation_id) == 0:
        # This case is theoretically possible only in case http_method and path_name are
        # sanitized down to empty string. According to the specs valid values of
        # http_method will not allow this case.
        raise ValueError(
            '_sanitize_operation_id produced an empty operation id starting from '
            'operation_id={operation_id}, http_method={http_method} and path_name={path_name}'.format(
                operation_id=operation_id,
                http_method=http_method,
                path_name=path_name,
            ),
        )

    return sanitized_operation_id


class Operation(object):

    def __init__(self, swagger_spec, path_name, http_method, op_spec):
        """Swagger operation defined by a unique (http_method, path_name) pair.

        :type swagger_spec: :class:`Spec`
        :param path_name: path of the operation. e.g. /pet/{petId}
        :param http_method: get/put/post/delete/etc
        :param op_spec: operation specification in dict form
        """
        self.swagger_spec = swagger_spec
        self.path_name = path_name
        self.http_method = http_method
        self.op_spec = swagger_spec.deref(op_spec)

        # (key, value) = (param name, Param)
        self.params = {}

    @cached_property
    def consumes(self):
        """Note that the operation can override the value defined globally
        at #/consumes.

        :return: List of supported mime types consumed by this operation. e.g.
            ["application/x-www-form-urlencoded"]
        :rtype: list of strings, never None
        """
        deref = self.swagger_spec.deref
        result = deref(self.op_spec.get('consumes'))
        if result is None:
            result = deref(self.swagger_spec._internal_spec_dict.get('consumes', []))
        return result

    @cached_property
    def security_specs(self):
        deref = self.swagger_spec.deref
        op_spec = deref(self.op_spec)
        spec_dict = deref(self.swagger_spec._internal_spec_dict)
        if 'security' in op_spec:
            return deref(op_spec['security'])
        else:
            return spec_dict.get('security', [])

    @cached_property
    def security_requirements(self):
        return [
            SecurityRequirement(self.swagger_spec, security_item)
            for security_item in self.security_specs
        ]

    @property
    def acceptable_security_definition_combinations(self):
        return sorted(sorted(security_item.keys()) for security_item in self.security_specs)

    @cached_property
    def security_parameters(self):
        return [
            Param(self.swagger_spec, self, parameter_dict)
            for security_requirement in self.security_requirements
            for parameter_dict in security_requirement.parameters_representation_dict
        ]

    @cached_property
    def produces(self):
        """Note that the operation can override the value defined globally
        at #/produces.

        :return: List of supported mime types produced by this operation. e.g.
            ["application/json"]
        :rtype: list of strings, never None
        """
        deref = self.swagger_spec.deref
        result = deref(self.op_spec.get('produces'))
        if result is None:
            return deref(self.swagger_spec._internal_spec_dict.get('produces', []))
        return result

    @classmethod
    def from_spec(cls, swagger_spec, path_name, http_method, op_spec):
        """
        Creates a :class:`Operation` and builds up its list of :class:`Param` s

        :param swagger_spec: :class:`Spec`
        :param path_name: path of the operation. e.g. /pet/{petId}
        :param http_method: get/put/post/delete/etc
        :param op_spec: operation specification in dict form
        :rtype: :class:`Operation`
        """
        op = cls(swagger_spec, path_name, http_method, op_spec)
        op.params = build_params(op)
        return op

    @cached_property
    def operation_id(self):
        """A friendly name for the operation. The id MUST be unique among all
        operations described in the API. Tools and libraries MAY use the
        operation id to uniquely identify an operation.

        This this field is not required, it will be generated when needed.

        :rtype: str
        """
        deref = self.swagger_spec.deref
        op_id = deref(self.op_spec.get('operationId'))
        return _sanitize_operation_id(op_id, self.http_method, self.path_name)

    def __repr__(self):
        return u"%s(%s)" % (self.__class__.__name__, self.operation_id)


def build_params(op):
    """Builds up the list of this operation's parameters taking into account
    parameters that may be available for this operation's path component.

    :type op: :class:`bravado_core.operation.Operation`

    :returns: dict where (k,v) is (param_name, Param)
    """
    swagger_spec = op.swagger_spec
    deref = swagger_spec.deref
    op_spec = deref(op.op_spec)
    op_params_spec = deref(op_spec.get('parameters', []))
    spec_dict = deref(swagger_spec._internal_spec_dict)
    paths_spec = deref(spec_dict.get('paths', {}))
    path_spec = deref(paths_spec.get(op.path_name))
    path_params_spec = deref(path_spec.get('parameters', []))

    # Order of addition is *important* here. Since op_params are last in the
    # list, they will replace any previously defined path_params with the
    # same name when the final params dict is constructed in the loop below.
    params_spec = path_params_spec + op_params_spec

    params = AliasKeyDict()
    for param_spec in params_spec:
        param = Param(swagger_spec, op, deref(param_spec))
        sanitized_name = sanitize_name(param.name)
        params[sanitized_name] = param
        params.add_alias(param.name, sanitized_name)

    # Security parameters cannot override and been overridden by operation or path objects
    new_params = {}
    new_param_aliases = {}
    for parameter in op.security_parameters:
        param_name = sanitize_name(parameter.name)
        if param_name in params:
            raise SwaggerSchemaError(
                "'{0}' security parameter is overriding a parameter defined in operation or path object".format(
                    parameter.name,
                )
            )
        else:
            # not directly in params because different security requirements could share parameters
            new_params[param_name] = parameter
            new_param_aliases[parameter.name] = param_name

    params.update(new_params)
    for alias, name in iteritems(new_param_aliases):
        params.add_alias(alias, name)
    return params
