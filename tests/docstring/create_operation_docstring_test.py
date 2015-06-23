# -*- coding: utf-8 -*-
from bravado_core.docstring import create_operation_docstring
from bravado_core.operation import Operation


def test_simple(op_spec, empty_swagger_spec):
    expected = \
        "[GET] Finds Pets by status\n\n" \
        "Multiple status values can be provided with comma " \
        "seperated strings\n\n" \
        ":param status: the status, yo! (Default: available) (optional)\n" \
        ":type status: array\n" \
        ":returns: 200: successful operation\n" \
        ":rtype: array:#/definitions/Pet\n" \
        ":returns: 400: Invalid status value\n"

    op = Operation(empty_swagger_spec, '/pet', 'get', op_spec)
    assert expected == create_operation_docstring(op)


def test_no_parameters(op_spec, empty_swagger_spec):
    del op_spec['parameters']
    expected = \
        "[GET] Finds Pets by status\n\n" \
        "Multiple status values can be provided with comma " \
        "seperated strings\n\n" \
        ":returns: 200: successful operation\n" \
        ":rtype: array:#/definitions/Pet\n" \
        ":returns: 400: Invalid status value\n"

    op = Operation(empty_swagger_spec, '/pet', 'get', op_spec)
    assert expected == create_operation_docstring(op)


def test_deprecated(op_spec, empty_swagger_spec):
    expected = \
        "** DEPRECATED **\n" \
        "[GET] Finds Pets by status\n\n" \
        "Multiple status values can be provided with comma " \
        "seperated strings\n\n" \
        ":param status: the status, yo! (Default: available) (optional)\n" \
        ":type status: array\n" \
        ":returns: 200: successful operation\n" \
        ":rtype: array:#/definitions/Pet\n" \
        ":returns: 400: Invalid status value\n"

    op_spec['deprecated'] = True
    op = Operation(empty_swagger_spec, '/pet', 'get', op_spec)
    assert expected == create_operation_docstring(op)


def test_no_summary(op_spec, empty_swagger_spec):
    expected = \
        "Multiple status values can be provided with comma " \
        "seperated strings\n\n" \
        ":param status: the status, yo! (Default: available) (optional)\n" \
        ":type status: array\n" \
        ":returns: 200: successful operation\n" \
        ":rtype: array:#/definitions/Pet\n" \
        ":returns: 400: Invalid status value\n"

    del op_spec['summary']
    op = Operation(empty_swagger_spec, '/pet', 'get', op_spec)
    assert expected == create_operation_docstring(op)


def test_no_description(op_spec, empty_swagger_spec):
    expected = \
        "[GET] Finds Pets by status\n\n" \
        ":param status: the status, yo! (Default: available) (optional)\n" \
        ":type status: array\n" \
        ":returns: 200: successful operation\n" \
        ":rtype: array:#/definitions/Pet\n" \
        ":returns: 400: Invalid status value\n"

    del op_spec['description']
    op = Operation(empty_swagger_spec, '/pet', 'get', op_spec)
    assert expected == create_operation_docstring(op)


def test_unicode(op_spec, empty_swagger_spec):
    # Only test freeform fields (those most likely to contain unicode)
    op_spec['summary'] = u'Ümlaut1'
    op_spec['description'] = u'Ümlaut2'
    op_spec['parameters'][0]['name'] = u'Ümlaut3'
    op_spec['parameters'][0]['description'] = u'Ümlaut4'
    op_spec['parameters'][0]['default'] = u'Ümlaut5'
    op_spec['responses']['200']['description'] = u'Ümlaut6'
    op_spec['responses']['400']['description'] = u'Ümlaut7'

    expected = \
        u"[GET] Ümlaut1\n\n" \
        u"Ümlaut2\n\n" \
        u":param Ümlaut3: Ümlaut4 (Default: Ümlaut5) (optional)\n" \
        u":type Ümlaut3: array\n" \
        u":returns: 200: Ümlaut6\n" \
        u":rtype: array:#/definitions/Pet\n" \
        u":returns: 400: Ümlaut7\n"

    op = Operation(empty_swagger_spec, '/pet', 'get', op_spec)
    assert expected == create_operation_docstring(op)
