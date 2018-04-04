# -*- coding: utf-8 -*-
import abc
import logging
from warnings import warn

import six
from six import iteritems

from bravado_core.schema import collapsed_properties
from bravado_core.schema import is_dict_like
from bravado_core.schema import is_list_like
from bravado_core.schema import SWAGGER_PRIMITIVES
from bravado_core.util import determine_object_type
from bravado_core.util import ObjectType
from bravado_core.util import sanitize_name
from bravado_core.util import strip_xscope


log = logging.getLogger(__name__)

# Models in #/definitions are tagged with this key so that they can be
# differentiated from 'object' types.
MODEL_MARKER = 'x-model'
MODEL_MARKER_BLESSED = 'x-model-blessed'


def _get_model_name(model_dict):
    """Determine model name from model dictionary representation and Swagger Path"""
    model_name = model_dict.get(MODEL_MARKER)
    if not model_name:
        model_name = model_dict.get('title')
    return model_name


def _generate_model_name(path):
    return sanitize_name('_'.join(path))


def _raise_or_warn_duplicated_model(swagger_spec, message):
    if swagger_spec.config['use_models']:
        raise ValueError(message)
    else:
        log.warning(message)
    return


def _register_visited_model(path, model_spec, model_name, visited_models, is_blessed, swagger_spec):
    """
    Register a model that has been tagged by a callback method.

    :param path: list of path segments to the key
    :type path: list
    :param model_spec: swagger specification of the model
    :type model_spec: dict
    :param model_name: name of the model to register
    :type model_name: str
    :param visited_models: models that have already been identified
    :type visited_models: dict (k,v) == (model_name, path)
    :param is_blessed: flag that determines if the model name has been obtained by blessing
    :type is_blessed: bool
    :type swagger_spec: :class:`bravado_core.spec.Spec`
    """
    log.debug('Found model: %s (is_blessed %s)', model_name, is_blessed)
    if model_name in visited_models:
        return _raise_or_warn_duplicated_model(
            swagger_spec=swagger_spec,
            message='Duplicate "{0}" model found at path {1}. Original "{0}" model at path {2}'.format(
                model_name, path, visited_models[model_name],
            ),
        )

    visited_models[model_name] = path
    model_spec[MODEL_MARKER] = model_name
    if is_blessed:
        model_spec[MODEL_MARKER_BLESSED] = True


def _unregister_visited_model(model_spec, model_name, visited_models):
    """
    Un-register a model that has been tagged by a callback method.

    :param model_spec: swagger specification of the model
    :type model_spec: dict
    :param model_name: name of the model to register
    :type model_name: str
    :param visited_models: models that have already been identified
    :type visited_models: dict (k,v) == (model_name, path)
    """
    model_spec.pop(MODEL_MARKER, None)
    visited_models.pop(model_name, None)
    is_blessed = model_spec.pop(MODEL_MARKER_BLESSED, False)
    log.debug('Unregistered model: %s (is_blessed %s)', model_name, is_blessed)


def tag_models(container, key, path, visited_models, swagger_spec):
    """
    Callback used during the swagger spec ingestion process to tag models
    with a 'x-model'. This is only done in the root document.

    A list of visited models is maintained to avoid duplication of tagging.

    NOTE: this callback tags models only if they are on the root of a swagger file
    in the definitions section (ie. (<swagger_file>)?#/definitions/<key>)).
    In order to tag the model with MODEL_MARKER the model (contained in container[key])
    need to represent an object.

    NOTE: tag_models has priority respects bless_models.
    So if a model_name (x-model) has been generated due to blessing it will be overridden by tag_models

    INFO: Implementation detail.
    Respect ``collect_models`` this callback gets executed on the model_spec's parent container.
    This is needed because this callback could modify (adding MODEL_MARKER) the model_spec;
    performing this operation when the container represents model_spec will generate errors
    because we're iterating over an object that gets mutated by the callback.

    :param container: container being visited
    :param key: attribute in container being visited as a string
    :param path: list of path segments to the key
    :type visited_models: dict (k,v) == (model_name, path)
    :type swagger_spec: :class:`bravado_core.spec.Spec`
    """
    if len(path) < 2 or path[-2] != 'definitions':
        return
    deref = swagger_spec.deref
    model_spec = deref(container.get(key))

    if not is_object(swagger_spec, model_spec):
        return

    model_name = deref(model_spec.get(MODEL_MARKER))
    if model_name is not None:
        # If x-model has not been blessed, the tag is correct
        if not deref(model_spec.get(MODEL_MARKER_BLESSED)):
            return
        # If x-model has been generated then remove it and use tag_models for the proper naming
        _unregister_visited_model(model_spec, model_name, visited_models)

    model_name = _get_model_name(model_spec) or key
    _register_visited_model(
        path=path,
        model_spec=model_spec,
        model_name=model_name,
        visited_models=visited_models,
        is_blessed=False,
        swagger_spec=swagger_spec,
    )


def bless_models(container, key, path, visited_models, swagger_spec):
    """
    Callback used during the swagger spec ingestion process to add
    ``x-model`` attribute to models which does not define it.

    The callbacks is in charge of adding MODEL_MARKER in case a model
    (identifies as an object of type SCHEMA) has enough information for
    determining a model name (ie. has ``title`` attribute defined)

    INFO: Implementation detail.
    Respect ``collect_models`` this callback gets executed on the model_spec's parent container.
    This is needed because this callback could modify (adding MODEL_MARKER) the model_spec;
    performing this operation when the container represents model_spec will generate errors
    because we're iterating over an object that gets mutated by the callback.

    :param container: container being visited
    :param key: attribute in container being visited as a string
    :param path: list of path segments to the key
    :type visited_models: dict (k,v) == (model_name, path)
    :type swagger_spec: :class:`bravado_core.spec.Spec`
    """
    if not is_dict_like(container):
        return

    deref = swagger_spec.deref
    model_spec = deref(container.get(key))

    if (
        not is_dict_like(model_spec) or
        not is_object(swagger_spec, model_spec, no_default_type=True) or
        # NOTE: determine_object_type uses a simple heuristic to determine if a model_spec has a SCHEMA type
        # for this reason is important that model_spec is recognized as model in the most accurate way
        # so we should not rely on default typing of a schema
        determine_object_type(model_spec) != ObjectType.SCHEMA or
        deref(model_spec.get(MODEL_MARKER)) is not None
    ):
        return

    model_name = _get_model_name(model_spec) or _generate_model_name(path)

    _register_visited_model(
        path=path,
        model_spec=model_spec,
        model_name=model_name,
        visited_models=visited_models,
        is_blessed=True,
        swagger_spec=swagger_spec,
    )


def collect_models(container, key, path, models, swagger_spec):
    """
    Callback used during the swagger spec ingestion to collect all the
    tagged models and create appropriate python types for them.

    NOTE: this callback creates the model python type only if the container
    represents a valid "model", the container has been marked with a model name
    (has MODEL_MARKER key) and the referenced model does not have the python
    model type generated.

    :param container: container being visited
    :param key: attribute in container being visited as a string
    :param path: list of path segments to the key
    :param models: created model types are placed here
    :type swagger_spec: :class:`bravado_core.spec.Spec`
    """
    if key == MODEL_MARKER and is_object(swagger_spec, container):
        model_spec = swagger_spec.deref(container)
        model_name = _get_model_name(container)
        model_type = models.get(model_name)
        if not model_type:
            models[model_name] = create_model_type(swagger_spec, model_name, model_spec)
        elif (
            # the condition with strip_xscope is the most selective check
            # but it implies memory allocation, so additional lightweight checks
            # are added to avoid strip_xscope check
            id(model_type._model_spec) != id(model_spec) and
            model_type._model_spec != model_spec and
            strip_xscope(model_type._model_spec) != strip_xscope(model_spec)
        ):
            return _raise_or_warn_duplicated_model(
                swagger_spec=swagger_spec,
                message='Identified duplicated model: model_name "{model_name}", path: {path}.\n'
                '    Known model spec: "{model_type._model_spec}"\n'
                '    New model spec: "{model_spec}"\n'
                'TIP: enforce different model naming by using {MODEL_MARKER}'.format(
                    path=path,
                    model_name=model_name,
                    model_type=model_type,
                    model_spec=model_spec,
                    MODEL_MARKER=MODEL_MARKER
                ),
            )


class ModelMeta(abc.ABCMeta):
    def __instancecheck__(self, instance):
        """
        An object is instance of a specific model class if:
        - model class and instance share the same model Swagger Specs
        - instance inherits from model class (in case of multiple inheritance, ie. allOff)
        """
        if not isinstance(type(instance), type(self)):
            return False

        if not hasattr(self, '_model_spec'):
            # This is the base Model class
            return True

        if not hasattr(instance, '_model_spec'):
            return False

        if self._model_spec == instance._model_spec:
            return True

        return self.__name__ in type(instance)._inherits_from


@six.add_metaclass(ModelMeta)
class Model(object):
    """Base class for Swagger models.

    Attribute access:

    Model property values can be accessed as attributes with the same name.
    Because there are no restrictions in the Swagger spec on the names of
    model properties, there is no way to avoid conflicts between those and
    the names of attributes used in the Python implementation of the model
    (methods, etc.). The solution here is to have all non-property attributes
    making up the public API of this class prefixed by a single underscore
    (this is done with the :func:`collections.namedtuple` type factory, which
    also uses property values with arbitrary names). There may still be name
    conflicts but only if the property name also begins with an underscore,
    which is uncommon. Truly private attributes are prefixed with double
    underscores in the source code (and thus by "_Model__" after
    `name-mangling`_).

    Attribute access has been modified somewhat from the Python default.
    Non-dynamic attributes like methods, etc. will always be returned over
    property values when there is a name conflict. To access a property
    explicitly use the ``model[prop_name]`` syntax as if it were a dictionary
    (setting and deleting properties also works).

    .. _name-mangling: https://docs.python.org/3.5/tutorial/classes.html#private-variables

    .. attribute:: _swagger_spec

        Class attribute that must be assigned on subclasses.
        :class:`bravado_core.spec.Spec` the model was created from.

    .. attribute:: _model_spec

        Class attribute that must be assigned on subclasses. JSON-like dict
        that describes the model.

    .. attribute:: _properties

        Class attribute that must be assigned on subclasses. Dict mapping
        property names to their specs. See
        :func:`bravado_core.schema.collapsed_properties`.
    """

    # Implementation details:
    #
    # Property value are stored in the __dict attribute. It would have also
    # been possible to use the instance's __dict__ itself except that then
    # __getattribute__ would have to have been overridden instead of
    # __getattr__.

    def __init__(self, **kwargs):
        """Initialize from property values in keyword arguments.

        :param \\**kwargs: Property values by name.
        """
        self.__init_from_dict(kwargs)

    def __init_from_dict(self, dct, include_missing_properties=True):
        """Initialize model from a dictionary of property values.

        :param dict dct: Dictionary of property values by name. They need not
            actually exist in :attr:`_properties`.
        """

        # Create the attribute value dictionary
        # We need bypass the overloaded __setattr__ method
        # Note the name mangling!
        object.__setattr__(self, '_Model__dict', dict())

        # Additional property names in dct
        additional = set(dct).difference(self._properties)

        if additional and not self._model_spec.get('additionalProperties', True):
            raise AttributeError(
                "Model {0} does not have attributes for: {1}"
                .format(type(self), list(additional))
            )

        # Assign properties in model_spec, filling in None if missing from dct
        for attr_name in self._properties:
            if include_missing_properties or attr_name in dct:
                self.__dict[attr_name] = dct.get(attr_name)

        # we've got additionalProperties to set on the model
        for attr_name in additional:
            self.__dict[attr_name] = dct[attr_name]

    def __contains__(self, obj):
        """Has a property set (including additional)."""
        return obj in self.__dict

    def __iter__(self):
        """Iterate over property names (including additional)."""
        return iter(self.__dict)

    def __getattr__(self, attr_name):
        """Only search through properties if attribute not found normally.

        :type attr_name: str
        """
        try:
            return self[attr_name]
        except KeyError:
            raise AttributeError(
                'type object {0!r} has no attribute {1!r}'
                .format(type(self).__name__, attr_name)
            )

    def __setattr__(self, attr_name, val):
        """Setting an attribute assigns a value to a property.

        :type attr_name: str
        """
        self[attr_name] = val

    def __delattr__(self, attr_name):
        """Deleting an attribute deletes the property (see __delitem__).

        :type attr_name: str
        """
        try:
            del self[attr_name]
        except KeyError:
            raise AttributeError(attr_name)

    def __getitem__(self, property_name):
        """Get a property value by name.

        :type attr_name: str
        """
        return self.__dict[property_name]

    def __setitem__(self, property_name, val):
        """Set a property value by name.

        :type attr_name: str
        """
        self.__dict[property_name] = val

    def __delitem__(self, property_name):
        """Unset a property by name.

        Additional properties will be deleted alltogether. Properties defined
        in the spec will be set to ``None``.

        :type attr_name: str
        """
        if property_name in self._properties:
            self.__dict[property_name] = None
        else:
            del self.__dict[property_name]

    def __eq__(self, other):
        """Check for equality with another instance.

        Two model instances are equal if they have the same type and the same
        properties and values (including additional properties).
        """
        # Check same type as self
        if type(self) is not type(other):
            return False

        # Ignore any '_raw' keys
        def norm_dict(d):
            return dict((k, d[k]) for k in d if k != '_raw')

        return norm_dict(self.__dict) == norm_dict(other.__dict)

    def __dir__(self):
        """Return only property names (including additional)."""
        return sorted(self.__dict.keys())

    def __repr__(self):
        """Return properties (including additional)."""
        s = [
            "{0}={1!r}".format(attr_name, self[attr_name])
            for attr_name in sorted(self.__dict.keys())
            if attr_name in self
        ]
        return "{0}({1})".format(self.__class__.__name__, ', '.join(s))

    @property
    def _additional_props(self):
        """Names of properties in instance which are not defined in spec."""
        return set(self.__dict).difference(self._properties)

    def _as_dict(self, additional_properties=True, recursive=True):
        """Get property values as dictionary.

        :param bool additional_properties: Whether to include additional properties
            set on the instance but not defined in the spec.
        :param bool recursive: Whether to convert all property values which
            are themselves models to dicts as well.

        :rtype: dict
        """

        dct = dict()
        for attr_name, attr_val in iteritems(self.__dict):
            if attr_name not in self._properties and not additional_properties:
                continue

            if recursive:
                is_list = is_list_like(attr_val)

                attribute = attr_val if is_list else [attr_val]

                new_attr_val = []
                for attr in attribute:
                    if isinstance(attr, Model):
                        attr = attr._as_dict(
                            additional_properties=additional_properties,
                            recursive=recursive,
                        )
                    new_attr_val.append(attr)

                attr_val = new_attr_val if is_list else new_attr_val[0]

            dct[attr_name] = attr_val

        return dct

    # provide the same interface as a namedtuple
    _asdict = _as_dict

    @classmethod
    def _from_dict(cls, dct):
        """Create a model instance from dictionary of property values.

        The only advantage of this over ``__init__(**dct)`` is that using
        the property name ``self`` will not result in an error.

        :param dict dct: Property values by name.
        :rtype: .Model
        """
        model = object.__new__(cls)
        model.__init_from_dict(
            dct=dct,
            include_missing_properties=cls._swagger_spec.config['include_missing_properties'],
        )
        return model

    def marshal(self):
        warn(
            "Model object methods are now prefixed with single underscore - use _marshal() instead.",
            DeprecationWarning,
        )
        return self._marshal()

    def _marshal(self):
        """Marshal into a json-like dict.

        :rtype: dict
        """
        from bravado_core.marshal import marshal_model
        return marshal_model(self._swagger_spec, self._model_spec, self)

    @classmethod
    def unmarshal(cls, val):
        warn(
            "Model object methods are now prefixed with single underscore - use _unmarshal() instead.",
            DeprecationWarning,
        )
        return cls._unmarshal(val)

    @classmethod
    def _unmarshal(cls, val):
        """Unmarshal a dict into an instance of the model.

        :type val: dict
        :rtype: .Model
        """
        from bravado_core.unmarshal import unmarshal_model
        return unmarshal_model(cls._swagger_spec, cls._model_spec, val)

    @classmethod
    def isinstance(cls, obj):
        warn(
            "Model object methods are now prefixed with single underscore - use _isinstance() instead.",
            DeprecationWarning,
        )
        return cls._isinstance(obj)

    @classmethod
    def _isinstance(cls, obj):
        warn(
            "_isinstance is deprecated. Please use isinstance(obj, cls) instead..",
            DeprecationWarning,
        )
        return isinstance(obj, cls)


class ModelDocstring(object):
    """Descriptor for model classes that dynamically generates docstrings.

    Docstrings are generated lazily the first time they are accessed, then
    stored in the ``__docstring__`` attribute of the class. Subsequent
    calls to :meth:`__get__` will return the stored value.

    Note that this can't just be used as a descriptor on the :class:`.Model`
    base class as all subclasses will automatically be given their own
    __doc__ attribute when the class is defined/created (set to ``None`` if no
    docstring present in the definition). This attribute is not writable and
    so cannot be deleted or changed. The only way around this is to supply
    an instance of this descriptor as the value for the ``__doc__`` attribute
    when each subclass is created.
    """

    def __get__(self, obj, cls):
        if not hasattr(cls, '__docstring__'):
            cls.__docstring__ = create_model_docstring(cls._swagger_spec,
                                                       cls._model_spec)

        return cls.__docstring__


def create_model_type(swagger_spec, model_name, model_spec, bases=(Model,)):
    """Create a dynamic class from the model data defined in the swagger
    spec.

    The docstring for this class is dynamically generated because generating
    the docstring is relatively expensive, and would only be used in rare
    cases for interactive debugging in a REPL.

    :type swagger_spec: :class:`bravado_core.spec.Spec`
    :param model_name: model name
    :param model_spec: json-like dict that describes a model.
    :param tuple bases: Base classes for type. At least one should be
        :class:`.Model` or a subclass of it.
    :returns: dynamic type inheriting from ``bases``.
    :rtype: type
    """

    inherits_from = []
    if 'allOf' in model_spec:
        for schema in model_spec['allOf']:
            inherited_name = swagger_spec.deref(schema).get(MODEL_MARKER, None)
            if inherited_name:
                inherits_from.append(inherited_name)

    return type(str(model_name), bases, dict(
        __doc__=ModelDocstring(),
        _swagger_spec=swagger_spec,
        _model_spec=model_spec,
        _properties=collapsed_properties(model_spec, swagger_spec),
        _inherits_from=inherits_from,
    ))


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


def is_object(swagger_spec, object_spec, no_default_type=False):
    """
    A schema definition is of type object if its type is object or if it uses
    model composition (i.e. it has an allOf property).
    :param swagger_spec: :class:`bravado_core.spec.Spec`
    :param object_spec: specification for a swagger object
    :type object_spec: dict
    :param no_default_type: ignore bravado-core 'default_type_to_object' configuration
    :type no_default_type: bool
    :return: True if the spec describes an object, False otherwise.
    """
    deref = swagger_spec.deref
    default_type = 'object' if not no_default_type and swagger_spec.config['default_type_to_object'] else None
    return deref(object_spec.get('type', default_type)) == 'object' or 'allOf' in object_spec


def create_model_docstring(swagger_spec, model_spec):
    """
    :type swagger_spec: :class:`bravado_core.spec.Spec`
    :param model_spec: specification for a model in dict form
    :rtype: string or unicode
    """
    deref = swagger_spec.deref
    model_spec = deref(model_spec)

    s = 'Attributes:\n\n\t'
    properties = collapsed_properties(model_spec, swagger_spec)
    attr_iter = iter(sorted(iteritems(properties)))
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
