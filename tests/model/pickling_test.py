# -*- coding: utf-8 -*-
from six import iterkeys
from six.moves.cPickle import dumps

from bravado_core.model import from_pickable_representation
from bravado_core.model import ModelDocstring
from bravado_core.model import to_pickable_representation


def test_ensure_pickable_representation_is_pickable(cat_type):
    pickable_representation = to_pickable_representation('Cat', cat_type)
    # Ensures that the pickle.dump of the pickable representation is pickable
    # If the dumps call does not raise an exception then we were able to pickle
    # the model type
    dumps(pickable_representation)


def test_ensure_that_get_model_type_from_pickable_representation_returns_the_original_model(cat_type):
    # Ensures that the pickle.dump of the pickable representation is pickable
    # If the dumps call does not raise an exception then we were able to pickle
    # the model type
    reconstructed_model_type = from_pickable_representation(
        model_pickable_representation=to_pickable_representation('Cat', cat_type),
    )
    assert reconstructed_model_type.__name__ == 'Cat'

    def is_the_same(attr_name):
        if attr_name == '_swagger_spec':
            return cat_type._swagger_spec.is_equal(reconstructed_model_type._swagger_spec)
        elif attr_name == '__doc__':
            return (
                isinstance(cat_type.__dict__[attr_name], ModelDocstring) and
                isinstance(reconstructed_model_type.__dict__[attr_name], ModelDocstring)
            )
        else:
            return cat_type.__dict__[attr_name] == reconstructed_model_type.__dict__[attr_name]

    assert [
        attribute_name
        for attribute_name in iterkeys(cat_type.__dict__)
        if not is_the_same(attribute_name)
    ] == []
