# -*- coding: utf-8 -*-
import logging

import typing


if typing.TYPE_CHECKING:
    from bravado_core.spec import Spec  # noqa: F401

    T = typing.TypeVar('T')

log = logging.getLogger(__name__)


class SecurityDefinition(object):
    """
    Wrapper of security definition object (http://swagger.io/specification/#securityDefinitionsObject)

    :type swagger_spec: :class:`bravado_core.spec.Spec`
    :type security_definition_spec: security definition specification in dict form
    """

    def __init__(self, swagger_spec, security_definition_spec):
        # type: (Spec, typing.Mapping[typing.Text, typing.Any]) -> None
        self.swagger_spec = swagger_spec
        self.security_definition_spec = swagger_spec.deref(security_definition_spec)

    @property
    def location(self):
        # type: () -> typing.Optional[typing.Text]
        # not using 'in' as the name since it is a keyword in python
        return self.security_definition_spec.get('in')

    @property
    def type(self):
        # type: () -> typing.Text
        return self.security_definition_spec['type']

    @property
    def name(self):
        # type: () -> typing.Optional[typing.Text]
        return self.security_definition_spec.get('name')

    @property
    def flow(self):
        # type: () -> typing.Optional[typing.Text]
        return self.security_definition_spec.get('flow')

    @property
    def scopes(self):
        # type: () -> typing.Optional[typing.List[typing.Text]]
        return self.security_definition_spec.get('scopes')

    @property
    def authorizationUrl(self):
        # type: () -> typing.Optional[typing.Text]
        return self.security_definition_spec.get('authorizationUrl')

    @property
    def tokenUrl(self):
        # type: () -> typing.Optional[typing.Text]
        return self.security_definition_spec.get('tokenUrl')

    @property
    def parameter_representation_dict(self):
        # type: () -> typing.Optional[typing.Mapping[typing.Text, typing.Any]]
        if self.type == 'apiKey':
            return {
                'required': False,
                'type': 'string',
                'description': self.security_definition_spec.get('description', ''),
                'name': self.name,
                'in': self.location,
            }
        else:
            return None
