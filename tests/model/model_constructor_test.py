import pytest

from mock import Mock
from bravado_core.spec import Spec


@pytest.fixture
def cat_kwargs():
    return {
        'id': 12,
        'category': {
            'id': 42,
            'name': 'Feline',
        },
        'name': 'Oskar',
        'photoUrls': ['example.com/img1', 'example.com/img2'],
        'tags': [
            {
                'id': 1,
                'name': 'cute'
            }
        ],
        'neutered': True,
    }


@pytest.fixture
def user_kwargs():
    return {
        'firstName': 'Darwin',
        'userStatus': 9,
        'id': 999,
    }


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
        user_type, user_kwargs):
    # verify exra kwargs are attached to the model as attributes when
    # additionalProperties is not present
    user_kwargs['foo'] = 'bar'
    user = user_type(**user_kwargs)
    assert user.foo == 'bar'
    assert 'foo' in dir(user)


def test_additionalProperties_true(user_type, user_kwargs):
    # verify exra kwargs are attached to the model as attributes when
    # additionalProperties is True
    user_type._model_spec['additionalProperties'] = True
    user_kwargs['foo'] = 'bar'  # additional prop
    user = user_type(**user_kwargs)
    assert user.foo == 'bar'
    assert 'foo' in dir(user)


def test_additionalProperties_false(user_type, user_kwargs):
    # verify exra kwargs are caught during model construction when
    # additionalProperties is False
    user_type._model_spec['additionalProperties'] = False
    user_kwargs['foo'] = 'bar'  # additional prop
    with pytest.raises(AttributeError) as excinfo:
        user_type(**user_kwargs)
    assert "does not have attributes for: ['foo']" in str(excinfo.value)


def test_allOf(cat_type, cat_kwargs):
    cat = cat_type(**cat_kwargs)
    assert cat.id == 12
    assert cat.category == {'id': 42, 'name': 'Feline'}
    assert cat.name == 'Oskar'
    assert cat.photoUrls == ['example.com/img1', 'example.com/img2']
    assert cat.tags == [{'id': 1, 'name': 'cute'}]
    assert cat.neutered is True
