# -*- coding: utf-8 -*-
from bravado_core.model import create_model_docstring


def test_pet(petstore_spec):
    model_spec = petstore_spec.spec_dict['definitions']['Pet']

    expected = (
        "Attributes:\n\n"
        "\tcategory: Category\n"
        "\tid: integer\n"
        "\tname: string\n"
        "\tphotoUrls: list of string\n"
        "\tstatus: string - pet status in the store\n"
        "\ttags: list of Tag\n"
        "\t"
    )
    docstring = create_model_docstring(model_spec)
    assert expected == docstring


def test_unicode(petstore_spec):
    model_spec = petstore_spec.spec_dict['definitions']['Pet']
    model_spec['properties']['status']['description'] = u'Ümlaut1'

    expected = (
        u"Attributes:\n\n"
        u"\tcategory: Category\n"
        u"\tid: integer\n"
        u"\tname: string\n"
        u"\tphotoUrls: list of string\n"
        u"\tstatus: string - Ümlaut1\n"
        u"\ttags: list of Tag\n"
        u"\t"
    )
    docstring = create_model_docstring(model_spec)
    assert expected == docstring
