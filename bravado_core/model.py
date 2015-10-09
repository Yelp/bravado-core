from functools import partial
import re

import jsonref
from six import iteritems

from bravado_core.docstring import docstring_property
from bravado_core.schema import (
    is_dict_like,
    is_list_like,
    SWAGGER_PRIMITIVES
)


# Models in #/definitions are tagged with this key so that they can be
# differentiated from 'object' types.
MODEL_MARKER = 'x-model'

RE_MODEL_NAME = re.compile(r"""
    [\w.]*              # Skip filename if specified
    \#/definitions/     # match `#/definitions/`
    (?P<model_name>\w+) # capture model_name
    $                   # end of string
""", re.VERBOSE)


def annotate_with_xmodel_callback(container, key):
    """Tags JsonRef proxies which represent Swagger models with
    'x-model': <model name>.

    :type container: list or dict
    :param key: the key of the object in the container to inspect
    :type key: string if container is a dict, int if container is a list
    """
    jsonref_proxy = container[key]
    if not isinstance(jsonref_proxy, jsonref.JsonRef):
        return

    ref_target = jsonref_proxy.__reference__['$ref']
    match = RE_MODEL_NAME.match(ref_target)
    if match is None:
        return

    model = jsonref_proxy.__subject__
    if is_dict_like(model) and MODEL_MARKER not in model:
        model[MODEL_MARKER] = match.group('model_name')


def fix_models_with_no_type_callback(container, key):
    """For models with no `type` specifier, default it to `object`.

    :type container: list or dict
    :param key: the key of the object in the container to inspect
    :type key: string if container is a dict, int if container is a list
    """
    jsonref_proxy = container[key]
    if not isinstance(jsonref_proxy, jsonref.JsonRef):
        return

    model = jsonref_proxy.__subject__
    if is_model(model) and 'type' not in model:
        model['type'] = 'object'


def create_reffed_models_callback(models, container, key):
    """Callback to build a model type for each jsonref_proxy that refers to a
    model. The passed in models dict is used to store the built model types.

    :type models: dict where (key, value) = (model_name, model_type)
    :type container: list or dict
    :param key: the key of the object in the container to inspect
    :type key: string if container is a dict, int if container is a list
    """
    jsonref_proxy = container[key]
    if not isinstance(jsonref_proxy, jsonref.JsonRef):
        return

    model = jsonref_proxy.__subject__
    if is_model(model):
        model_name = model[MODEL_MARKER]
        if model_name not in models:
            models[model_name] = create_model_type(model_name, model)


def create_dereffed_models_callback(models, container, key):
    """Callback to build a model type for each dict that represents a model.
    The passed in models dict is used to store the built model types.

    :type models: dict where (key, value) = (model_name, model_type)
    :type container: list or dict
    :param key: the key of the object in the container to inspect
    :type key: string if container is a dict, int if container is a list
    """
    if key != MODEL_MARKER:
        return

    model_name = container[key]
    if model_name not in models:
        models[model_name] = create_model_type(model_name, container)


def create_model_type(model_name, model_spec):
    """Create a dynamic class from the model data defined in the swagger
    spec.

    The docstring for this class is dynamically generated because generating
    the docstring is relatively expensive, and would only be used in rare
    cases for interactive debugging in a REPL.

    :param model_name: model name
    :param model_spec: json-like dict that describes a model.
    :returns: dynamic type created with attributes, docstrings attached
    :rtype: type
    """
    methods = dict(
        __doc__=docstring_property(partial(create_model_docstring, model_spec)),
        __eq__=lambda self, other: compare(self, other),
        __init__=lambda self, **kwargs: model_constructor(self, model_spec,
                                                          kwargs),
        __repr__=lambda self: create_model_repr(self, model_spec),
        __dir__=lambda self: model_dir(self, model_spec),
    )
    return type(str(model_name), (object,), methods)


def model_dir(model, model_spec):
    """Responsible for returning the names of the valid attributes on this
    model object.  This includes any properties defined in this model's spec
    plus additional attibutes that exist as `additionalProperties`.

    :param model: instance of a model
    :param model_spec: spec the passed in model in dict form
    :returns: list of str
    """
    return list(model_spec['properties'].keys()) + model._additional_props


def compare(first, second):
    """Compares two model types for equivalence.

    TODO: If a type composes another model type, .__dict__ recurse on those
          and compare again on those dict values.

    :param first: generated model type
    :type first: type
    :param second: generated model type
    :type second: type
    :returns: True if equivalent, False otherwise
    """
    if not hasattr(first, '__dict__') or not hasattr(second, '__dict__'):
        return False

    # Ignore any '_raw' keys
    def norm_dict(d):
        return dict((k, d[k]) for k in d if k != '_raw')

    return norm_dict(first.__dict__) == norm_dict(second.__dict__)


def model_constructor(model, model_spec, constructor_kwargs):
    """Constructor for the given model instance. Just assigns kwargs as attrs
    on the model based on the 'properties' in the model specification.

    :param model: Instance of a model type
    :type model: type
    :param model_spec: model specification
    :type model_spec: dict
    :param constructor_kwargs: kwargs sent in to the constructor invocation
    :type constructor_kwargs: dict
    :raises: AttributeError on constructor_kwargs that don't exist in the
        model specification's list of properties
    """
    arg_names = list(constructor_kwargs.keys())

    for attr_name, attr_spec in iteritems(model_spec['properties']):
        if attr_name in arg_names:
            attr_value = constructor_kwargs[attr_name]
            arg_names.remove(attr_name)
        else:
            attr_value = None
        setattr(model, attr_name, attr_value)

    if arg_names and not model_spec.get('additionalProperties', True):
        raise AttributeError(
            "Model {0} does not have attributes for: {1}"
            .format(type(model), arg_names))

    # we've got additionalProperties to set on the model
    for arg_name in arg_names:
        setattr(model, arg_name, constructor_kwargs[arg_name])

    # stash so that dir(model) works
    model._additional_props = arg_names


def create_model_repr(model, model_spec):
    """Generates the repr string for the model.

    :param model: Instance of a model
    :param model_spec: model specification
    :type model_spec: dict
    :returns: repr string for the model
    """
    s = [
        "{0}={1!r}".format(attr_name, getattr(model, attr_name))
        for attr_name in sorted(model_spec['properties'].keys())
    ]
    return "{0}({1})".format(model.__class__.__name__, ', '.join(s))


def fix_malformed_model_refs(spec):
    """jsonref doesn't understand  { $ref: Category } so just fix it up to
    { $ref: #/definitions/Category } when the ref name matches a #/definitions
    name. Yes, this is hacky!

    :param spec: Swagger spec in dict form
    """
    # TODO: fix this in a sustainable way in a fork of jsonref and try to
    #       upstream
    # TODO: unit test
    model_names = [model_name for model_name in spec.get('definitions', {})]

    def descend(fragment):
        if is_dict_like(fragment):
            for k, v in iteritems(fragment):
                if k == '$ref' and v in model_names:
                    fragment[k] = "#/definitions/{0}".format(v)
                descend(v)
        elif is_list_like(fragment):
            for element in fragment:
                descend(element)

    descend(spec)


def is_model(spec):
    """
    :param spec: specification for a swagger object
    :type spec: dict
    :return: True if the spec has been "marked" as a model type.
    """
    return MODEL_MARKER in spec


def create_model_docstring(model_spec):
    """
    :param model_spec: specification for a model in dict form
    :rtype: string or unicode
    """
    s = 'Attributes:\n\n\t'
    attr_iter = iter(sorted(iteritems(model_spec['properties'])))
    # TODO: Add more stuff available in the spec - 'required', 'example', etc
    for attr_name, attr_spec in attr_iter:
        schema_type = attr_spec['type']

        if schema_type in SWAGGER_PRIMITIVES:
            # TODO: update to python types and take 'format' into account
            attr_type = schema_type

        elif schema_type == 'array':
            array_spec = attr_spec['items']
            if is_model(array_spec):
                array_type = array_spec[MODEL_MARKER]
            else:
                array_type = array_spec['type']
            attr_type = u'list of {0}'.format(array_type)

        elif is_model(attr_spec):
            attr_type = attr_spec[MODEL_MARKER]

        elif schema_type == 'object':
            attr_type = 'dict'

        s += u'{0}: {1}'.format(attr_name, attr_type)

        if attr_spec.get('description'):
            s += u' - {0}'.format(attr_spec['description'])

        s += '\n\t'
    return s
