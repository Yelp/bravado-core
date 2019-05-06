# -*- coding: utf-8 -*-
import pytest

from bravado_core.exception import SwaggerSchemaError
from bravado_core.spec import build_api_serving_url


@pytest.fixture
def origin_url():
    return 'http://www.foo.com:80/bar/api-docs'


def test_no_overrides(origin_url):
    spec = {}
    assert 'http://www.foo.com:80/' == build_api_serving_url(spec, origin_url)


def test_override_host(origin_url):
    spec = {'host': 'womble.com'}
    api_serving_url = build_api_serving_url(spec, origin_url)
    assert 'http://womble.com/' == api_serving_url


def test_override_basepath(origin_url):
    spec = {'basePath': '/v1'}
    api_serving_url = build_api_serving_url(spec, origin_url)
    assert 'http://www.foo.com:80/v1' == api_serving_url


def test_use_spec_url_True():
    api_serving_url = build_api_serving_url(
        {},
        use_spec_url_for_base_path=True,
    )
    assert 'http://localhost/' == api_serving_url


def test_use_spec_url_True_when_basePath_present():
    api_serving_url = build_api_serving_url({'basePath': '/v1'},
                                            use_spec_url_for_base_path=True)
    assert 'http://localhost/v1' == api_serving_url


def test_use_spec_url_True_when_origin_url_present(origin_url):
    api_serving_url = build_api_serving_url({}, origin_url,
                                            use_spec_url_for_base_path=True)
    assert 'http://www.foo.com:80/bar/api-docs' == api_serving_url


def test_use_spec_url_True_when_basePath_and_origin_url_present(origin_url):
    api_serving_url = build_api_serving_url({'basePath': '/v1'}, origin_url,
                                            use_spec_url_for_base_path=True)
    assert 'http://www.foo.com:80/v1' == api_serving_url


def test_use_spec_url_False():
    api_serving_url = build_api_serving_url({},
                                            use_spec_url_for_base_path=False)
    assert 'http://localhost/' == api_serving_url


def test_use_spec_url_False_when_basePath_present():
    api_serving_url = build_api_serving_url({'basePath': '/v1'},
                                            use_spec_url_for_base_path=False)
    assert 'http://localhost/v1' == api_serving_url


def test_use_spec_url_False_when_origin_url_present(origin_url):
    api_serving_url = build_api_serving_url({}, origin_url,
                                            use_spec_url_for_base_path=False)
    assert 'http://www.foo.com:80/' == api_serving_url


def test_use_spec_url_False_when_basePath_and_origin_url_present(origin_url):
    api_serving_url = build_api_serving_url({'basePath': '/v1'}, origin_url,
                                            use_spec_url_for_base_path=True)
    assert 'http://www.foo.com:80/v1' == api_serving_url


def test_override_scheme(origin_url):
    spec = {'schemes': ['https']}
    api_serving_url = build_api_serving_url(spec, origin_url)
    assert 'https://www.foo.com:80/' == api_serving_url


def test_override_scheme_multiple_schemes(origin_url):
    spec = {'schemes': ['https', 'ws']}
    api_serving_url = build_api_serving_url(spec, origin_url)
    assert 'https://www.foo.com:80/' == api_serving_url


def test_pick_preferred_scheme(origin_url):
    spec = {'schemes': ['http', 'https']}
    api_serving_url = build_api_serving_url(
        spec, origin_url, preferred_scheme='https')
    assert 'https://www.foo.com:80/' == api_serving_url


def test_pick_origin_scheme_when_preferred_scheme_none(origin_url):
    spec = {'schemes': ['http', 'https']}
    api_serving_url = build_api_serving_url(spec, origin_url)
    assert 'http://www.foo.com:80/' == api_serving_url


def test_preferred_scheme_not_available(origin_url):
    spec = {'schemes': ['https']}
    with pytest.raises(SwaggerSchemaError) as excinfo:
        build_api_serving_url(spec, origin_url, preferred_scheme='ws')
    assert 'not supported' in str(excinfo.value)


def test_origin_url_None():
    assert 'http://localhost/' == build_api_serving_url({})
