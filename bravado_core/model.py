from functools import partial
import logging

from six import iteritems

from bravado_core.docstring import docstring_property
from bravado_core.schema import SWAGGER_PRIMITIVES


log = logging.getLogger(__name__)

# Models in #/definitions are tagged with this key so that they can be
# differentiated from 'object' types.
MODEL_MARKER = 'x-model'


def tag_models(container, key, path, visited_models, swagger_spec):
    """Callback used during the swagger spec ingestion process to tag models
    with a 'x-model'. This is only done in the root document.

    A list of visited models is maintained to avoid duplication of tagging.

    :param container: container being visited
    :param key: attribute in container being visited as a string
    :param path: list of path segments to the key
    :type visited_models: dict (k,v) == (model_name, path)
    :type swagger_spec: :class:`bravado_core.spec.Spec`
    """
    if len(path) < 2 or path[-2] != 'definitions':
        return
    deref = swagger_spec.deref
    model_name = key
    model_spec = deref(container.get(key))

    if deref(model_spec.get('type')) != 'object':
        return

    if deref(model_spec.get(MODEL_MARKER)) is not None:
        return

    log.debug('Found model: {0}'.format(model_name))
    if model_name in visited_models:
        raise ValueError(
            'Duplicate "{0}" model found at path {1}. '
            'Original "{0}" model at path {2}'
            .format(model_name, path, visited_models[model_name]))

    model_spec['x-model'] = model_name
    visited_models[model_name] = path


def collect_models(container, key, path, models, swagger_spec):
    """Callback used during the swagger spec ingestion to collect all the
    tagged models and create appropriate python types for them.

    :param container: container being visited
    :param key: attribute in container being visited as a string
    :param path: list of path segments to the key
    :param models: created model types are placed here
    :type swagger_spec: :class:`bravado_core.spec.Spec`
    """
    deref = swagger_spec.deref
    if key == MODEL_MARKER:
        model_spec = container
        model_name = deref(model_spec.get(MODEL_MARKER))
        models[model_name] = create_model_type(
            swagger_spec, model_name, model_spec)


def create_model_type(swagger_spec, model_name, model_spec):
    """Create a dynamic class from the model data defined in the swagger
    spec.

    The docstring for this class is dynamically generated because generating
    the docstring is relatively expensive, and would only be used in rare
    cases for interactive debugging in a REPL.

    :type swagger_spec: :class:`bravado_core.spec.Spec`
    :param model_name: model name
    :param model_spec: json-like dict that describes a model.
    :returns: dynamic type created with attributes, docstrings attached
    :rtype: type
    """
    doc = docstring_property(partial(
        create_model_docstring, swagger_spec, model_spec))

    methods = dict(
        __doc__=doc,
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


def is_model(swagger_spec, schema_object_spec):
    """
    :param swagger_spec: :class:`bravado_core.spec.Spec`
    :param schema_object_spec: specification for a swagger object
    :type schema_object_spec: dict
    :return: True if the spec has been "marked" as a model type, false
        otherwise.
    """
    deref = swagger_spec.deref
    schema_object_spec = deref(schema_object_spec)
    return deref(schema_object_spec.get(MODEL_MARKER)) is not None


def create_model_docstring(swagger_spec, model_spec):
    """
    :type swagger_spec: :class:`bravado_core.spec.Spec`
    :param model_spec: specification for a model in dict form
    :rtype: string or unicode
    """
    deref = swagger_spec.deref
    model_spec = deref(model_spec)

    s = 'Attributes:\n\n\t'
    attr_iter = iter(sorted(iteritems(model_spec['properties'])))
    # TODO: Add more stuff available in the spec - 'required', 'example', etc
    for attr_name, attr_spec in attr_iter:
        attr_spec = deref(attr_spec)
        schema_type = deref(attr_spec['type'])

        if schema_type in SWAGGER_PRIMITIVES:
            # TODO: update to python types and take 'format' into account
            attr_type = schema_type

        elif schema_type == 'array':
            array_spec = deref(attr_spec['items'])
            if is_model(swagger_spec, array_spec):
                array_type = deref(array_spec[MODEL_MARKER])
            else:
                array_type = deref(array_spec['type'])
            attr_type = u'list of {0}'.format(array_type)

        elif is_model(swagger_spec, attr_spec):
            attr_type = deref(attr_spec[MODEL_MARKER])

        elif schema_type == 'object':
            attr_type = 'dict'

        s += u'{0}: {1}'.format(attr_name, attr_type)

        if deref(attr_spec.get('description')):
            s += u' - {0}'.format(deref(attr_spec['description']))

        s += '\n\t'
    return s
