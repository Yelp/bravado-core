Changelog
=========
.. Make sure to link Issue and PR information as `(PR|Issue) #xxx`_ and with a link at the bottom of the document

5.13.1 (2019-06-12)
-------------------
- Fix ``isinstance`` regression - `PR #345`_

5.13.0 (2019-06-03)
-------------------
| The release is mainly based on performance improvements of marshalling and unmarshalling processes.

- ``Model`` instances use ``__slots__`` and ``@lazy_class_attribute`` to reduce ``Model`` class footprint - `PR #330`_
- ``unmarshal_schema_object`` honours the additional properties and default values - `PR #333`_
- ``unmarshal_model``/``unmarshal_object`` do not raise ``SwaggerMappingError`` in case of unknown polymorphic objects (better distinction between unmarshalling and validating processes) - `PR #333`_
- Refactor ``bravado_core.unmarshal`` module to enhance runtime performances - `PR #336`_
- ``@memoize_by_id`` performance improvements when used with ``kwargs`` only - `PR #337`_
- Refactor ``bravado_core.marshal`` module to enhance runtime performance - `PR #339`_

5.12.1 (2019-05-07)
-------------------
- Prevent ``DeprecationWarning`` in Python 3.7 - `PR #326`_
- Ensure compatibility with Windows Platform - `PR #327`_, `PR #328`_

5.12.0 (2019-04-10)
-------------------
- Allow ``Spec`` subclasses to provide their own ``$ref`` handlers - `PR #323`_
- Fix model name and model discovery bugs, better logic for including models in flattened spec - `PR #324`_
- Add deepcopy support to ``Model`` instances - `PR #325`_

5.11.0 (2019-03-08)
-------------------
- Do not throw ``SwaggerMappingError`` in case of missing body with optional body parameter - `Issue #321`_, `PR #322`_

5.10.2 (2019-03-06)
-------------------
- Fix issue with jsonschema 3.0 compatibility on Python 2.7 - `Issue #318`_, `PR #319`_, `PR #320`_

5.10.1 (2019-01-15)
-------------------
- Ensure that flattening Swagger Spec with ``$ref: None`` will not cause unbounded recursion - `PR #315`_
- Enhance ``is_ref`` detection to recognize only objects with ``$ref`` attribute and ``string`` value as reference - `PR #315`_

5.10.0 (2018-11-20)
-------------------
- Add ``use_spec_url_for_base_path`` configuration option - `PR #300`_ - Thanks DStape for your contribution!
- Ensure ``jsonschema >= 3`` compatibility - `PR #304`_
- Minor improvement on discriminator validation - `PR #302`_

5.0.7 (2018-09-18)
------------------
- Fix security object validation issue - `PR #294`_
- Fix unbounded recursion during object validation (if ``internally_dereference_refs`` is enabled) - `PR #297`_
- Fix api_url generation - `PR #295`_. Thanks mulmschneider for your contribution!

5.0.6 (2018-08-06)
------------------
- Swagger Spec flattening - fix regression that led to some model definitions not having the ``x-model`` marker anymore - `PR #293`_
- Fix marshalling of array params that use collectionFormat ``multi`` - `PR #292`_

5.0.5 (2018-08-02)
------------------
- Swagger Spec flattening - use model names instead of generated keys - `PR #284`_
- Swagger Spec flattening - replace inline models with top level definitions - `PR #285`_
- Fix query parameter marshalling in case of boolean parameters - `Issue #281`_ - `PR #286`_

5.0.4 (2018-06-29)
------------------
- Properly sanitize names with multiple leading digits, handle more edge cases correctly - `PR #282`_

5.0.3 (2018-06-06)
------------------
- Make sure spaces in path param values are quoted using percent notation instead of using ``+``. `Issue #278`_, `PR #279`_

5.0.2 (2018-06-04)
------------------
- Fix regression if ``internally_dereference_refs`` is used. `Issue #275`_, `PR #276`_

5.0.1 (2018-05-30)
------------------
- No longer make sure that all config keys are known; this allows users of the library to store additional configuration. - `PR #274`_

5.0.0 (2018-05-30)
------------------
- Refactor: model discovery is now handled in ``bravado_core.model`` - `PR #270`_
- Remove deprecated methods from Model type - `PR #270`_
- Remove deprecated parameters from ``bravado_core.spec_flattening.flattened_spec`` - `PR #269`_
- Ensure that models in ``#/definitions`` of referenced files are discovered - `PR #273`_

.. warning::
    This release contains breaking changes!
    The signature of ``bravado_core.spec_flattening.flattened_spec`` has been updated.
    The following methods have been removed from the public interface: ``bravado_core.model.tag_models``, ``bravado_core.model.bless_models``, ``bravado_core.model.collect_models`` and ``bravado_core.spec.post_process_spec``.

4.13.4 (2018-05-24)
-------------------
- Fix marshalling and unmarshalling of optional body parameters. `PR #268`_

4.13.3 (2018-05-16)
-------------------
- Add support for Content-Disposition filename - `PR #262`_. Thanks elmirjagudin for your contribution!
- Improve specs  flattening and dereferencing in case of relative references - `PR #263`_

4.13.2 (2018-03-19)
-------------------
- Fix bug where multiple schemes in the spec would sometimes cause a ``SwaggerSchemaError`` - `PR #260`_

4.13.1 (2018-03-02)
-------------------
- Catch TypeErrors during param unmarshalling, allowing JSON Schema to handle the error - `Issue #258`_, `PR #259`_. Thanks Nick DiRienzo for your contribution!

4.13.0 (2018-02-23)
-------------------
- Models are generated only for objects - `PR #246`_.
- Fix: ensure that models do not have references if ``internally_dereference_refs`` is used - `PR #247`_.
- Model name detection uses title attribute too - `PR #249`_.
- Duplicated models do not raise exception if ``use_models`` is not used - `PR #253`_.
- Alert or warn if pre-tagged duplicate models are found - `PR #254`_.

4.12.1 (2018-02-07)
-------------------
- Make sure unsanitized param names are used when unmarshalling a request - `PR #245`_.
- Expose the determine_object_type method as part of our API - `PR #244`_.

4.12.0 (2018-02-06)
-------------------
- Sanitize resource and parameter names so that they're valid Python identifiers. It uses the same logic as for operationIds - invalid characters are replaced with underscores,
  multiple consecutive underscores are merged into one, and leading / trailing underscores are removed. Using the unsanitized names will still work - `Issue #200`_, `PR #243`_.
- Allow overriding built-in default formats - `Issue #235`_, `PR #240`_. Thanks Brian J. Dowling for your contribution!
- Include additionalProperties in a models' __repr__ - `PR #242`_. Thanks again Brian J. Dowling!

4.11.5 (2018-01-30)
-------------------
- Use yaml.safe_load for parsing specs - `PR #241`_.

4.11.4 (2018-01-19)
-------------------
- Properly quote request parameters sent as part of the URL path - `PR #237`_, `PR #238`_.

4.11.3 (2018-01-16)
-------------------
- Remove strict isinstance check when marshalling models - `PR #236`_.

4.11.2 (2018-01-08)
-------------------
- Ensure ``internally_dereference_refs`` works with recursive specs - `PR #234`_.

4.11.1 (2017-12-18)
-------------------
- Speed up marshalling and unmarshalling of objects - `PR #226`_.
- Use ``msgpack-python`` instead of ``u-msgpack-python`` for performance improvements - `Issue #227`_, `PR #228`_.

4.11.0 (2017-11-09)
-------------------
- Add support for msgpack in responses (i.e. when unmarshalling) - `Issue #214`_, `PR #216`_.
- Improve performance by removing debug logging when dereferencing - `PR #208`_.

4.10.1 (2017-11-06)
-------------------
- Don't remove unrecognized configs; fixes compatibility with bravado - `PR #218`_.

4.10.0 (2017-11-03)
-------------------
- New config ``internally_dereference_refs`` that can significantly speed up unmarshalling. Currently disabled by default - `PR #204`_.
- Added support for new extension ``x-sensitive`` to scrub sensitive values from validation errors. Please check the `Sensitive Data`_ documentation for further details - `PR #213`_.
- Fixed an issue that would cause validation errors if ``obj_type`` was ``None`` - `PR #196`_.
- Fixed handling of defaults for array parameters - `PR #199`_.
- Performance improvements - `PR #207`_.

4.9.1 (2017-09-19)
------------------
- Properly marshal a model even if it's not created from the same ``Spec`` instance - `PR #194`_.

4.9.0 (2017-09-11)
------------------
- ``type`` is no longer required. By default, validation will not be performed if ``type`` is omitted. This is configurable with ``default_type_to_object`` - `Issue #166`_, `PR #192`_, `PR #183`_, `PR #193`_

4.8.4 (2017-09-06)
------------------
- Make sure all models are properly tagged when flattening the spec - `PR #191`_.

4.8.3 (2017-09-05)
------------------
- Improve spec flattening: recognize response objects and expose un-referenced models - `PR #184`_.
- Fix a bug when marshalling properties with no spec that have the value ``None`` - `PR #189`_.

4.8.2 (2017-09-04)
------------------
- Fix marshalling of ``null`` values for properties with ``x-nullable`` set to ``true`` - `Issue #185`_, `PR #186`_. Thanks Jan Baraniewski for the contribution!
- Add ``_asdict()`` method to each model, similar to what namedtuples have - `PR #188`_.

4.8.1 (2017-08-24)
------------------
- Make unmarshalling objects roughly 30% faster - `PR #182`_.

4.8.0 (2017-07-15)
------------------
- Add support for Swagger spec flattening - `PR #177`_.
- Fix handling of API calls that return non-JSON content (specifically text content) - `PR #175`_. Thanks mostrows2 for your contribution!
- Fix error message text when trying to unmarshal an invalid model - `PR #179`_.

4.7.3 (2017-05-05)
------------------
- Fix support for object composition (allOf) for data passed in the request body - `PR #167`_. Thanks Zi Li for your contribution!
- Return the default value for an optional field missing in the response - `PR #171`_.

4.7.2 (2017-03-23)
------------------
- Fix unmarshalling of null values for properties with no spec - `Issue #163`_, `PR #165`_.

4.7.1 (2017-03-22)
------------------
- Fix backward-incompatible Model API change which renames all model methods to have a single underscore infront of them. A deprecation warning has been added - `Issue #160`_, `PR #161`_. Thanks Adam Ever-Hadani for the contribution!

4.7.0 (2017-03-21)
------------------
- Added support for nullable fields in the format validator - `PR #143`_. Thanks Adam Ever-Hadani
- Add include_missing_properties configuration - `PR #152`_
- Consider default when unmarshalling - `PR #154`_
- Add discriminator support - `PR #128`_, `PR #159`_. Thanks Michael Jared Lumpe for your contribution
- Make sure pre-commit hooks are installed and run when running tests - `PR #155`_, `PR #158`_

4.6.1 (2017-02-15)
------------------
- Fix unmarshalling empty array types - `PR #148`_
- Removed support for Python 2.6 - `PR #147`_

4.6.0 (2016-11-28)
------------------
- Security Requirement validation (for ApiKey) - `PR #124`_
- Allow self as name for model property, adds new "create" alternate model constructor - `Issue #125`_, `PR #126`_.
- Allow overriding of security specs - `PR #121`_
- Adds minimal support for responses with text/* content_type.

4.5.1 (2016-09-27)
------------------
- Add marshal and unmarshal methods to models - `PR #113`_, `PR #120`_.

4.5.0 (2016-09-12)
------------------
- Support for model composition through the allOf property - `Issue #7`_, `PR #63`_, `PR #110`_. Thanks David Bartle for the initial contribution!
- Fix issue with header parameter values being non-string types - `PR #115`_.

4.4.0 (2016-08-26)
------------------
- Adds support for security scheme definitions, mostly focusing on the "apiKey" type - `PR #112`_.

4.3.2 (2016-08-17)
------------------
- Fixes around unmarshalling, x-nullable and required behavior - `Issue #108`_, `PR #109`_. Big thanks to Zachary Roadhouse for the report and pull request!
- Fix AttributeError when trying to unmarshal a required array param that's not present - `PR #111`_.

4.3.1 (2016-08-09)
------------------
- Check if a parameter is bool-type before assuming it's a string - `PR #107`_. Thanks to Nick DiRienzo for the pull request!

4.3.0 (2016-08-04)
------------------
- Add support for ``x-nullable`` - `Issue #47`_, `PR #64`_ and `PR #103`_. Thanks to Andreas Hug for the pull request!
- Fix support for vendor extensions at the path level - `PR #95`_, `PR #106`_. Thanks to Mikołaj Siedlarek for the initial pull request!

4.2.5 (2016-07-27)
------------------
- Add basepython python2.7 for flake8, docs, and coverage tox commands

4.2.4 (2016-07-26)
------------------
- coverage v4.2 was incompatible and was breaking the build. Added --append for the fix.

4.2.3 (2016-07-26)
------------------
- Accept tuples as a type list as well.

4.2.2 (2016-04-01)
------------------
- Fix marshalling of an optional array query parameter when not passed in the
  service call - `PR #87`_

4.2.1 (2016-03-23)
------------------
- Fix optional enums in request params - `Issue #77`_
- Fix resolving refs during validation - `Issue #82`_

4.2.0 (2016-03-10)
------------------
- More robust handling of operationId which contains non-standard chars - `PR #76`_
- Provide a client ingestible version of spec_dict with x-scope metadata removed. Accessible as Spec.client_spec_dict - `Issue #78`_

4.1.0 (2016-03-01)
------------------
- Better handling of query parameters that don't have a value - `Issue #68`_
- Allow marshalling of objects which are subclasses of dict - `PR #61`_
- Fix boolean query params to support case-insensetive true/false and 0/1 - `Issue #70`_
- Support for Swagger specs in yaml format - `Issue #42`_
- Fix validation of server side request parameters when collectionFormat=multi and item type is not string - `Issue #66`_
- Fix unmarshalling of server side request parameters when collectionFormat=multi and cardinality is one - `PR #75`_

4.0.1 (2016-01-11)
------------------
- Fix unmarshalling of an optional array query parameter when not passed in the
  query string.

4.0.0 (2015-11-17)
------------------
- Support for recursive $refs - `Issue #35`_
- Requires swagger-spec-validator 2.0.1
- Unqualified $refs no longer supported.
  Bad:  ``{"$ref": "User"}``
  Good: ``{"$ref": "#/definitions/User"}``
- Automatic tagging of models is only supported in the root swagger spec file.
  If you have models defined in $ref targets that are in other files, you must
  manually tag them with 'x-model' for them to be available as python types.
  See `Model Discovery`_ for more info.

3.1.1 (2015-10-19)
------------------
- Fix the creation of operations that contain shared parameters for a given endpoint.

3.1.0 (2015-10-19)
------------------
- Added http ``headers`` to ``bravado_core.response.IncomingResponse``.

3.0.2 (2015-10-12)
------------------
- Added docs on how to use `User-Defined Formats`_.
- Added docs on how to `Configure`_ bravado-core.
- formats added as a config option


3.0.1 (2015-10-09)
------------------
- Automatically tag models in external $refs - `Issue #45`_ - see `Model Discovery`_ for more info.

3.0.0 (2015-10-07)
------------------
- User-defined formats are now scoped to a Swagger spec - `Issue #50`_ (this is a non-backwards compatible change)
- Deprecated bravado_core.request.RequestLike and renamed to bravado_core.request.IncomingRequest
- Added ``make docs`` target and updated docs (still needs a lot of work though)

2.4.1 (2015-09-30)
------------------
- Fixed validation of user-defined formats - `Issue #48`_

2.4.0 (2015-08-13)
------------------
- Support relative '$ref' external references in swagger.json
- Fix dereferencing of jsonref when given in a list

2.3.0 (2015-08-10)
------------------
- Raise MatchingResponseNotFound instead of SwaggerMappingError
  when a response can't be matched to the Swagger schema.

2.2.0 (2015-08-06)
------------------
- Add reason to IncomingResponse

2.1.0 (2015-07-17)
------------------
- Handle user defined formats for serialization and validation.

2.0.0 (2015-07-13)
------------------
- Move http invocation to bravado
- Fix unicode in model docstrings
- Require swagger-spec-validator 1.0.12 to pick up bug fixes

1.1.0 (2015-06-25)
------------------
- Better unicode support
- Python 3 support

1.0.0-rc2 (2015-06-01)
----------------------
- Fixed file uploads when marshalling a request
- Renamed ResponseLike to IncomingResponse
- Fixed repr of a model when it has an attr with a unicode value

1.0.0-rc1 (2015-05-26)
----------------------
- Use basePath when matching an operation to a request
- Refactored exception hierarchy
- Added use_models config option

0.1.0 (2015-05-13)
------------------
- Initial release

.. Links Section
.. _Issue #7: https://github.com/Yelp/bravado-core/issue/7
.. _Issue #35: https://github.com/Yelp/bravado-core/issue/35
.. _Issue #42: https://github.com/Yelp/bravado-core/issue/42
.. _Issue #45: https://github.com/Yelp/bravado-core/issue/45
.. _Issue #47: https://github.com/Yelp/bravado-core/issue/47
.. _Issue #48: https://github.com/Yelp/bravado-core/issue/48
.. _Issue #50: https://github.com/Yelp/bravado-core/issue/50
.. _Issue #66: https://github.com/Yelp/bravado-core/issue/66
.. _Issue #68: https://github.com/Yelp/bravado-core/issue/68
.. _Issue #70: https://github.com/Yelp/bravado-core/issue/70
.. _Issue #77: https://github.com/Yelp/bravado-core/issue/77
.. _Issue #78: https://github.com/Yelp/bravado-core/issue/78
.. _Issue #82: https://github.com/Yelp/bravado-core/issue/82
.. _Issue #108: https://github.com/Yelp/bravado-core/issue/108
.. _Issue #125: https://github.com/Yelp/bravado-core/issue/125
.. _Issue #160: https://github.com/Yelp/bravado-core/issue/160
.. _Issue #163: https://github.com/Yelp/bravado-core/issue/163
.. _Issue #166: https://github.com/Yelp/bravado-core/issue/166
.. _Issue #185: https://github.com/Yelp/bravado-core/issue/185
.. _Issue #200: https://github.com/Yelp/bravado-core/issue/200
.. _Issue #214: https://github.com/Yelp/bravado-core/issue/214
.. _Issue #227: https://github.com/Yelp/bravado-core/issue/227
.. _Issue #235: https://github.com/Yelp/bravado-core/issue/235
.. _Issue #258: https://github.com/Yelp/bravado-core/issue/258
.. _Issue #275: https://github.com/Yelp/bravado-core/issue/275
.. _Issue #278: https://github.com/Yelp/bravado-core/issue/278
.. _Issue #281: https://github.com/Yelp/bravado-core/issue/281
.. _Issue #318: https://github.com/Yelp/bravado-core/issue/318
.. _Issue #321: https://github.com/Yelp/bravado-core/issue/321
.. _PR #61: https://github.com/Yelp/bravado-core/pull/61
.. _PR #63: https://github.com/Yelp/bravado-core/pull/63
.. _PR #64: https://github.com/Yelp/bravado-core/pull/64
.. _PR #75: https://github.com/Yelp/bravado-core/pull/75
.. _PR #76: https://github.com/Yelp/bravado-core/pull/76
.. _PR #87: https://github.com/Yelp/bravado-core/pull/87
.. _PR #95: https://github.com/Yelp/bravado-core/pull/95
.. _PR #103: https://github.com/Yelp/bravado-core/pull/103
.. _PR #106: https://github.com/Yelp/bravado-core/pull/106
.. _PR #107: https://github.com/Yelp/bravado-core/pull/107
.. _PR #109: https://github.com/Yelp/bravado-core/pull/109
.. _PR #110: https://github.com/Yelp/bravado-core/pull/110
.. _PR #111: https://github.com/Yelp/bravado-core/pull/111
.. _PR #112: https://github.com/Yelp/bravado-core/pull/112
.. _PR #113: https://github.com/Yelp/bravado-core/pull/113
.. _PR #115: https://github.com/Yelp/bravado-core/pull/115
.. _PR #120: https://github.com/Yelp/bravado-core/pull/120
.. _PR #121: https://github.com/Yelp/bravado-core/pull/121
.. _PR #124: https://github.com/Yelp/bravado-core/pull/124
.. _PR #126: https://github.com/Yelp/bravado-core/pull/126
.. _PR #128: https://github.com/Yelp/bravado-core/pull/128
.. _PR #143: https://github.com/Yelp/bravado-core/pull/143
.. _PR #147: https://github.com/Yelp/bravado-core/pull/147
.. _PR #148: https://github.com/Yelp/bravado-core/pull/148
.. _PR #152: https://github.com/Yelp/bravado-core/pull/152
.. _PR #154: https://github.com/Yelp/bravado-core/pull/154
.. _PR #155: https://github.com/Yelp/bravado-core/pull/155
.. _PR #158: https://github.com/Yelp/bravado-core/pull/158
.. _PR #159: https://github.com/Yelp/bravado-core/pull/159
.. _PR #161: https://github.com/Yelp/bravado-core/pull/161
.. _PR #165: https://github.com/Yelp/bravado-core/pull/165
.. _PR #167: https://github.com/Yelp/bravado-core/pull/167
.. _PR #171: https://github.com/Yelp/bravado-core/pull/171
.. _PR #175: https://github.com/Yelp/bravado-core/pull/175
.. _PR #177: https://github.com/Yelp/bravado-core/pull/177
.. _PR #179: https://github.com/Yelp/bravado-core/pull/179
.. _PR #182: https://github.com/Yelp/bravado-core/pull/182
.. _PR #183: https://github.com/Yelp/bravado-core/pull/183
.. _PR #184: https://github.com/Yelp/bravado-core/pull/184
.. _PR #186: https://github.com/Yelp/bravado-core/pull/186
.. _PR #188: https://github.com/Yelp/bravado-core/pull/188
.. _PR #189: https://github.com/Yelp/bravado-core/pull/189
.. _PR #191: https://github.com/Yelp/bravado-core/pull/191
.. _PR #192: https://github.com/Yelp/bravado-core/pull/192
.. _PR #193: https://github.com/Yelp/bravado-core/pull/193
.. _PR #194: https://github.com/Yelp/bravado-core/pull/194
.. _PR #196: https://github.com/Yelp/bravado-core/pull/196
.. _PR #199: https://github.com/Yelp/bravado-core/pull/199
.. _PR #204: https://github.com/Yelp/bravado-core/pull/204
.. _PR #207: https://github.com/Yelp/bravado-core/pull/207
.. _PR #208: https://github.com/Yelp/bravado-core/pull/208
.. _PR #213: https://github.com/Yelp/bravado-core/pull/213
.. _PR #216: https://github.com/Yelp/bravado-core/pull/216
.. _PR #218: https://github.com/Yelp/bravado-core/pull/218
.. _PR #226: https://github.com/Yelp/bravado-core/pull/226
.. _PR #228: https://github.com/Yelp/bravado-core/pull/228
.. _PR #234: https://github.com/Yelp/bravado-core/pull/234
.. _PR #236: https://github.com/Yelp/bravado-core/pull/236
.. _PR #237: https://github.com/Yelp/bravado-core/pull/237
.. _PR #238: https://github.com/Yelp/bravado-core/pull/238
.. _PR #240: https://github.com/Yelp/bravado-core/pull/240
.. _PR #241: https://github.com/Yelp/bravado-core/pull/241
.. _PR #242: https://github.com/Yelp/bravado-core/pull/242
.. _PR #243: https://github.com/Yelp/bravado-core/pull/243
.. _PR #244: https://github.com/Yelp/bravado-core/pull/244
.. _PR #245: https://github.com/Yelp/bravado-core/pull/245
.. _PR #246: https://github.com/Yelp/bravado-core/pull/246
.. _PR #247: https://github.com/Yelp/bravado-core/pull/247
.. _PR #249: https://github.com/Yelp/bravado-core/pull/249
.. _PR #253: https://github.com/Yelp/bravado-core/pull/253
.. _PR #254: https://github.com/Yelp/bravado-core/pull/254
.. _PR #259: https://github.com/Yelp/bravado-core/pull/259
.. _PR #260: https://github.com/Yelp/bravado-core/pull/260
.. _PR #262: https://github.com/Yelp/bravado-core/pull/262
.. _PR #263: https://github.com/Yelp/bravado-core/pull/263
.. _PR #268: https://github.com/Yelp/bravado-core/pull/268
.. _PR #269: https://github.com/Yelp/bravado-core/pull/269
.. _PR #270: https://github.com/Yelp/bravado-core/pull/270
.. _PR #273: https://github.com/Yelp/bravado-core/pull/273
.. _PR #274: https://github.com/Yelp/bravado-core/pull/274
.. _PR #276: https://github.com/Yelp/bravado-core/pull/276
.. _PR #279: https://github.com/Yelp/bravado-core/pull/279
.. _PR #282: https://github.com/Yelp/bravado-core/pull/282
.. _PR #284: https://github.com/Yelp/bravado-core/pull/284
.. _PR #285: https://github.com/Yelp/bravado-core/pull/285
.. _PR #286: https://github.com/Yelp/bravado-core/pull/286
.. _PR #292: https://github.com/Yelp/bravado-core/pull/292
.. _PR #293: https://github.com/Yelp/bravado-core/pull/293
.. _PR #294: https://github.com/Yelp/bravado-core/pull/294
.. _PR #295: https://github.com/Yelp/bravado-core/pull/295
.. _PR #297: https://github.com/Yelp/bravado-core/pull/297
.. _PR #300: https://github.com/Yelp/bravado-core/pull/300
.. _PR #302: https://github.com/Yelp/bravado-core/pull/302
.. _PR #304: https://github.com/Yelp/bravado-core/pull/304
.. _PR #315: https://github.com/Yelp/bravado-core/pull/315
.. _PR #319: https://github.com/Yelp/bravado-core/pull/319
.. _PR #320: https://github.com/Yelp/bravado-core/pull/320
.. _PR #322: https://github.com/Yelp/bravado-core/pull/322
.. _PR #323: https://github.com/Yelp/bravado-core/pull/323
.. _PR #324: https://github.com/Yelp/bravado-core/pull/324
.. _PR #325: https://github.com/Yelp/bravado-core/pull/325
.. _PR #326: https://github.com/Yelp/bravado-core/pull/326
.. _PR #327: https://github.com/Yelp/bravado-core/pull/327
.. _PR #328: https://github.com/Yelp/bravado-core/pull/328
.. _PR #330: https://github.com/Yelp/bravado-core/pull/330
.. _PR #333: https://github.com/Yelp/bravado-core/pull/333
.. _PR #336: https://github.com/Yelp/bravado-core/pull/336
.. _PR #337: https://github.com/Yelp/bravado-core/pull/337
.. _PR #339: https://github.com/Yelp/bravado-core/pull/339
.. _PR #345: https://github.com/Yelp/bravado-core/pull/345


.. Link To Documentation pages
.. _Configure: https://bravado-core.readthedocs.org/en/latest/config.html
.. _Model Discovery: https://bravado-core.readthedocs.org/en/latest/models.html#model-discovery
.. _User-Defined Formats: https://bravado-core.readthedocs.org/en/latest/formats.html
.. _Sensitive Data: https://bravado-core.readthedocs.io/en/latest/models.html#sensitive-data
