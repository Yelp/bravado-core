# -*- coding: utf-8 -*-
import pytest

from bravado_core.schema import collapsed_properties


def test_simple(user_type, user_kwargs):
    user = user_type(**user_kwargs)
    assert user.firstName == 'Darwin'
    assert user.userStatus == 9
    assert user.id == 999
    assert user.lastName is None
    assert user.email is None
    assert user.password is None


def test_empty_kwargs(user_type):
    user = user_type()
    assert user.firstName is None
    assert user.userStatus is None
    assert user.id is None
    assert user.lastName is None
    assert user.email is None
    assert user.password is None


def test_additionalProperties_defaults_to_true_when_not_present(
        user_type, user_kwargs,
):
    # verify exra kwargs are attached to the model as attributes when
    # additionalProperties is not present
    user_kwargs['foo'] = 'bar'
    user = user_type(**user_kwargs)
    assert user.foo == 'bar'
    assert 'foo' in dir(user)


def test_additionalProperties_true(definitions_spec, user_type, user_kwargs):
    # verify exra kwargs are attached to the model as attributes when
    # additionalProperties is True
    user_type._model_spec['additionalProperties'] = True
    user_kwargs['foo'] = 'bar'  # additional prop
    user = user_type(**user_kwargs)
    assert user.foo == 'bar'
    assert 'foo' in dir(user)
    assert set(user) == set(definitions_spec['User']['properties'].keys()).union({'foo'})


def test_additionalProperties_false(user_type, user_kwargs):
    # verify exra kwargs are caught during model construction when
    # additionalProperties is False
    user_type._model_spec['additionalProperties'] = False
    user_kwargs['foo'] = 'bar'  # additional prop
    with pytest.raises(AttributeError) as excinfo:
        user_type(**user_kwargs)
    assert "does not have attributes for: ['foo']" in str(excinfo.value)


def test_allOf(cat_swagger_spec, cat_type, cat_kwargs):
    cat = cat_type(**cat_kwargs)
    assert cat.id == 12
    assert cat.category == {'id': 42, 'name': 'Feline'}
    assert cat.name == 'Oskar'
    assert cat.photoUrls == ['example.com/img1', 'example.com/img2']
    assert cat.tags == [{'id': 1, 'name': 'cute'}]
    assert cat.neutered is True
    assert set(cat) == set(
        collapsed_properties(
            cat_swagger_spec.spec_dict['definitions']['Cat'], cat_swagger_spec,
        ).keys(),
    )
