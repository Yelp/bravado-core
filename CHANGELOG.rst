Changelog
=========

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
