from collections import defaultdict
import logging

from six import iteritems

from bravado_core.exception import SwaggerMappingError
from bravado_core.operation import Operation

log = logging.getLogger(__name__)


def convert_path_to_resource(path_name):
    """
    Given a path name (#/paths/{path_name}) try to convert it into a resource
    name on a best effort basis when an operation has no tags.

    Examples:
      /pet                ->  pet
      /pet/findByStatus   ->  pet
      /pet/findByTags     ->  pet
      /pet/{petId}        ->  pet

    :param path_name: #/paths/{path_name} from a swagger spec
    :return: name of the resource to which operations under the given path
        should be associated with.
    """
    tokens = path_name.lstrip('/').split('/')
    err_msg = "Could not extract resource name from path {0}"
    resource_name = tokens[0]
    if not resource_name:
        raise SwaggerMappingError(err_msg.format(path_name))
    return resource_name


def build_resources(swagger_spec):
    """Transforms the REST resources in the json-like swagger_spec into rich
    :Resource: objects that have associated :Operation:s.

    :type swagger_spec: :class:`bravado_core.spec.Spec`
    :returns: dict where (key,value) = (resource name, Resource)
    """
    # Map operations to resources using operation tags if available.
    # - If an operation has multiple tags, it will be associated with multiple
    #   resources!
    # - If an operation has no tags, its resource name will be derived from its
    #   path
    # key = tag_name   value = { operation_id : Operation }
    tag_to_operations = defaultdict(dict)
    paths = swagger_spec.spec_dict['paths']
    for path_name, path_spec in iteritems(paths):
        for http_method, operation_spec in iteritems(path_spec):
            if http_method == 'parameters':
                continue

            operation = Operation.from_spec(
                swagger_spec, path_name, http_method, operation_spec)
            tags = operation_spec.get('tags', [])

            if not tags:
                tags.append(convert_path_to_resource(path_name))

            for tag in tags:
                tag_to_operations[tag][operation.operation_id] = operation

    resources = {}
    for tag, operations in iteritems(tag_to_operations):
        resources[tag] = Resource(tag, operations)
    return resources


class Resource(object):
    """
    A Swagger resource is associated with multiple operations.
    """
    def __init__(self, name, operations):
        """
        :param name: resource name
        :type name: str
        :param operations: operations associated with this resource (by tag)
        :type operations: dict where (key, value) = (op_name, Operation)
        """
        log.debug(u"Building resource '%s'" % name)
        self.name = name
        self.operations = operations

    def __repr__(self):
        return u"%s(%s)" % (self.__class__.__name__, self.name)

    def __getattr__(self, item):
        """
        :param item: name of the operation to return
        :rtype: :class:`bravado_core.operation.Operation`
        """
        op = self.operations.get(item)
        if not op:
            raise AttributeError(u"Resource '%s' has no operation '%s'" %
                                 (self.name, item))
        return op

    def __dir__(self):
        """
        :return: list of operation names
        """
        return self.operations.keys()
