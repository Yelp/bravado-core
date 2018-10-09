Changelog
=========

5.0.7 (2018-09-18)
------------------
- Fix security object validation issue - PR #294
- Fix unbounded recursion during object validation (if ``internally_dereference_refs`` is enabled) - PR #297
- Fix api_url generation - PR #295. Thanks mulmschneider for your contribution!

5.0.6 (2018-08-06)
------------------
- Swagger Spec flattening - fix regression that led to some model definitions not having the ``x-model`` marker anymore - PR #293
- Fix marshalling of array params that use collectionFormat ``multi`` - PR #292

5.0.5 (2018-08-02)
------------------
- Swagger Spec flattening - use model names instead of generated keys - PR #284
- Swagger Spec flattening - replace inline models with top level definitions - PR #285
- Fix query parameter marshalling in case of boolean parameters - Issue #281 - PR #286

5.0.4 (2018-06-29)
------------------
- Properly sanitize names with multiple leading digits, handle more edge cases correctly - PR #282

5.0.3 (2018-06-06)
------------------
- Make sure spaces in path param values are quoted using percent notation instead of using ``+``. Issue #278, PR #279

5.0.2 (2018-06-04)
------------------
- Fix regression if `internally_dereference_refs` is used. Issue #275, PR #276

5.0.1 (2018-05-30)
------------------
- No longer make sure that all config keys are known; this allows users of the library to store additional configuration. - PR #274

5.0.0 (2018-05-30)
------------------
- Refactor: model discovery is now handled in ``bravado_core.model`` - PR #270
- Remove deprecated methods from Model type - PR #270
- Remove deprecated parameters from ``bravado_core.spec_flattening.flattened_spec`` - PR #269
- Ensure that models in `#/definitions` of referenced files are discovered - PR #273

.. warning::
    This release contains breaking changes!
    The signature of ``bravado_core.spec_flattening.flattened_spec`` has been updated.
    The following methods have been removed from the public interface: ``bravado_core.model.tag_models``, ``bravado_core.model.bless_models``, ``bravado_core.model.collect_models`` and ``bravado_core.spec.post_process_spec``.

4.13.4 (2018-05-24)
-------------------
- Fix marsharling and unmarshaling of optional body parameters. PR #268

4.13.3 (2018-05-16)
-------------------
- Add support for Content-Disposition filename - PR #262. Thanks elmirjagudin for your contribution!
- Improve specs  flattening and dereferencing in case of relative references - PR #263

4.13.2 (2018-03-19)
-------------------
- Fix bug where multiple schemes in the spec would sometimes cause a ``SwaggerSchemaError`` - PR #260

4.13.1 (2018-03-02)
-------------------
- Catch TypeErrors during param unmarshalling, allowing JSON Schema to handle the error - Issue #258, PR #259. Thanks Nick DiRienzo for your contribution!

4.13.0 (2018-02-23)
-------------------
- Models are generated only for objects - PR #246.
- Fix: ensure that models do not have references if ``internally_dereference_refs`` is used - PR #247.
- Model name detection uses title attribute too - PR #249.
- Duplicated models do not raise exception if ``use_models`` is not used - PR #253.
- Alert or warn if pre-tagged duplicate models are found - PR #254.

4.12.1 (2018-02-07)
-------------------
- Make sure unsanitized param names are used when unmarshalling a request - PR #245.
- Expose the determine_object_type method as part of our API - PR #244.

4.12.0 (2018-02-06)
-------------------
- Sanitize resource and parameter names so that they're valid Python identifiers. It uses the same logic as for operationIds - invalid characters are replaced with underscores,
  multiple consecutive underscores are merged into one, and leading / trailing underscores are removed. Using the unsanitized names will still work - Issue #200, PR #243.
- Allow overriding built-in default formats - Issue #235, PR #240. Thanks Brian J. Dowling for your contribution!
- Include additionalProperties in a models' __repr__ - PR #242. Thanks again Brian J. Dowling!

4.11.5 (2018-01-30)
-------------------
- Use yaml.safe_load for parsing specs - PR #241.

4.11.4 (2018-01-19)
-------------------
- Properly quote request parameters sent as part of the URL path - PR #237, #238.

4.11.3 (2018-01-16)
-------------------
- Remove strict isinstance check when marshalling models - PR #236.

4.11.2 (2018-01-08)
-------------------
- Ensure ``internally_dereference_refs`` works with recursive specs - PR #234.

4.11.1 (2017-12-18)
-------------------
- Speed up marshalling and unmarshalling of objects - PR #226.
- Use msgpack-python instead of u-msgpack-python for performance improvements - Issue #227, PR #228.

4.11.0 (2017-11-09)
-------------------
- Add support for msgpack in responses (i.e. when unmarshalling) - Issue #214, PR #216.
- Improve performance by removing debug logging when dereferencing - PR #208.

4.10.1 (2017-11-06)
-------------------
- Don't remove unrecognized configs; fixes compatibility with bravado - PR #218.

4.10.0 (2017-11-03)
-------------------
- New config ``internally_dereference_refs`` that can significantly speed up unmarshalling. Currently disabled by default - PR #204.
- Added support for new extension ``x-sensitive`` to scrub sensitive values from validation errors. Please check the `documentation <http://bravado-core.readthedocs.io/en/latest/models.html#sensitive-data>`_ for further details - PR #213.
- Fixed an issue that would cause validation errors if ``obj_type`` was ``None`` - PR #196.
- Fixed handling of defaults for array parameters - PR #199.
- Performance improvements - PR #207.

4.9.1 (2017-09-19)
------------------
- Properly marshal a model even if it's not created from the same ``Spec`` instance - PR #194.

4.9.0 (2017-09-11)
------------------
- ``type`` is no longer required. By default, validation will not be performed if ``type`` is omitted. This is configurable with ``default_type_to_object`` - Issue #166, #192, PR #183, #193

4.8.4 (2017-09-06)
------------------
- Make sure all models are properly tagged when flattening the spec - PR #191.

4.8.3 (2017-09-05)
------------------
- Improve spec flattening: recognize response objects and expose un-referenced models - PR #184.
- Fix a bug when marshalling properties with no spec that have the value ``None`` - PR #189.

4.8.2 (2017-09-04)
------------------
- Fix marshalling of ``null`` values for properties with ``x-nullable`` set to ``true`` - Issue #185, PR #186. Thanks Jan Baraniewski for the contribution!
- Add ``_asdict()`` method to each model, similar to what namedtuples have - PR #188.

4.8.1 (2017-08-24)
------------------
- Make unmarshalling objects roughly 30% faster - PR #182.

4.8.0 (2017-07-15)
------------------
- Add support for Swagger spec flattening - PR #177.
- Fix handling of API calls that return non-JSON content (specifically text content) - PR #175. Thanks mostrows2 for your contribution!
- Fix error message text when trying to unmarshal an invalid model - PR #179.

4.7.3 (2017-05-05)
------------------
- Fix support for object composition (allOf) for data passed in the request body - PR #167. Thanks Zi Li for your contribution!
- Return the default value for an optional field missing in the response - PR #171.

4.7.2 (2017-03-23)
------------------
- Fix unmarshalling of null values for properties with no spec - Issue #163, PR #165.

4.7.1 (2017-03-22)
------------------
- Fix backward-incompatible Model API change which renames all model methods to have a single underscore infront of them. A deprecation warning has been added - Issue #160, PR #161. Thanks Adam Ever-Hadani for the contribution!

4.7.0 (2017-03-21)
------------------
- Added support for nullable fields in the format validator - PR #143. Thanks Adam Ever-Hadani
- Add include_missing_properties configuration - PR #152
- Consider default when unmarshalling - PR #154
- Add discriminator support - PR #128, #159. Thanks Michael Jared Lumpe for your contribution
- Make sure pre-commit hooks are installed and run when running tests - PR #155, #158

4.6.1 (2017-02-15)
------------------
- Fix unmarshalling empty array types - PR #148
- Removed support for Python 2.6 - PR #147

4.6.0 (2016-11-28)
------------------
- Security Requirement validation (for ApiKey) - PR #124
- Allow self as name for model property, adds new "create" alternate model constructor - Issue #125, PR #126.
- Allow overriding of security specs - PR #121
- Adds minimal support for responses with text/* content_type.

4.5.1 (2016-09-27)
------------------
- Add marshal and unmarshal methods to models - PR #113, #120.

4.5.0 (2016-09-12)
------------------
- Support for model composition through the allOf property - Issue #7, PR #63, #110. Thanks David Bartle for the initial contribution!
- Fix issue with header parameter values being non-string types - PR #115.

4.4.0 (2016-08-26)
------------------
- Adds support for security scheme definitions, mostly focusing on the "apiKey" type - PR #112.

4.3.2 (2016-08-17)
------------------
- Fixes around unmarshalling, x-nullable and required behavior - Issue #108, PR #109. Big thanks to Zachary Roadhouse for the report and pull request!
- Fix AttributeError when trying to unmarshal a required array param that's not present - PR #111.

4.3.1 (2016-08-09)
------------------
- Check if a parameter is bool-type before assuming it's a string - PR #107. Thanks to Nick DiRienzo for the pull request!

4.3.0 (2016-08-04)
------------------
- Add support for ``x-nullable`` - Issue #47, PR #64 and #103. Thanks to Andreas Hug for the pull request!
- Fix support for vendor extensions at the path level - PR #95, #106. Thanks to Mikołaj Siedlarek for the initial pull request!

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
  service call - PR #87

4.2.1 (2016-03-23)
------------------
- Fix optional enums in request params - Issue #77
- Fix resolving refs during validation - Issue #82

4.2.0 (2016-03-10)
------------------
- More robust handling of operationId which contains non-standard chars - PR #76
- Provide a client ingestible version of spec_dict with x-scope metadata removed. Accessible as Spec.client_spec_dict - Issue #78

4.1.0 (2016-03-01)
------------------
- Better handling of query parameters that don't have a value - Issue #68
- Allow marshalling of objects which are subclasses of dict - PR #61
- Fix boolean query params to support case-insensetive true/false and 0/1 - Issue #70
- Support for Swagger specs in yaml format - Issue #42
- Fix validation of server side request parameters when collectionFormat=multi and item type is not string - Issue #66
- Fix unmarshaling of server side request parameters when collectionFormat=multi and cardinality is one - PR #75

4.0.1 (2016-01-11)
------------------
- Fix unmarshalling of an optional array query parameter when not passed in the
  query string.

4.0.0 (2015-11-17)
------------------
- Support for recursive $refs - Issue #35
- Requires swagger-spec-validator 2.0.1
- Unqualified $refs no longer supported.
  Bad:  ``{"$ref": "User"}``
  Good: ``{"$ref": "#/definitions/User"}``
- Automatic tagging of models is only supported in the root swagger spec file. 
  If you have models defined in $ref targets that are in other files, you must 
  manually tag them with 'x-model' for them to be available as python types.
  See `Model Discovery <http://bravado-core.readthedocs.org/en/latest/models.html#model-discovery>`_ 
  for more info.

3.1.1 (2015-10-19)
------------------
- Fix the creation of operations that contain shared parameters for a given endpoint.

3.1.0 (2015-10-19)
------------------
- Added http ``headers`` to ``bravado_core.response.IncomingResponse``.

3.0.2 (2015-10-12)
------------------
- Added docs on how to use `user-defined formats <http://bravado-core.readthedocs.org/en/latest/formats.html>`_.
- Added docs on how to `configure <http://bravado-core.readthedocs.org/en/latest/config.html>`_ bravado-core.
- `formats` added as a config option

3.0.1 (2015-10-09)
------------------
- Automatically tag models in external $refs - Issue #45 - see `Model Discovery <http://bravado-core.readthedocs.org/en/latest/models.html#model-discovery>`_ for more info.

3.0.0 (2015-10-07)
------------------
- User-defined formats are now scoped to a Swagger spec - Issue #50 (this is a non-backwards compatible change)
- Deprecated bravado_core.request.RequestLike and renamed to bravado_core.request.IncomingRequest
- Added `make docs` target and updated docs (still needs a lot of work though)

2.4.1 (2015-09-30)
------------------
- Fixed validation of user-defined formats - Issue #48

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
- Fixed file uploads when marshaling a request
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
