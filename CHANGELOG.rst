Changelog
=========

- The content will be used to build the Changelog for the new bravado-core release
- Fix handling of API calls that return non-JSON content (specifically text content).
  (add before this line your modifications summary and PR reference)

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
