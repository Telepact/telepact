BUILT_FILE = .built
CODEGEN_PYPROJECT = ../../../tool/uapicodegen/pyproject.toml
JAVA_POM_FILE = ../../../lib/java/pom.xml

.PHONY: all dep

all: dep $(BUILT_FILE)

$(BUILT_FILE): $(CODEGEN_PYPROJECT) $(JAVA_POM_FILE)
	poetry lock
	poetry install
	poetry run python -m uapicodegen --schema-dir ../../test/schema/example --lang java --out src/gen/java/uapitest --package uapitest
	touch $(BUILT_FILE)
	UAPI_VERSION=$$(cd ../../../lib/java && uapi-version get) && uapi-version depset $$UAPI_VERSION || (echo "Install uapi-version bump with 'pipx install ../../tool/uapi_version'" && exit 1)


dep:
	cd ../../../tool/uapicodegen && make
	cd ../../../lib/java && make

