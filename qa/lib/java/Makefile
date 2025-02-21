BUILT_FILE = .built
CODEGEN_PYPROJECT = ../../../tool/uapicodegen/pyproject.toml
JAVA_POM_FILE = ../../../lib/java/pom.xml

.PHONY: all dep

all: dep $(BUILT_FILE)

$(BUILT_FILE): $(CODEGEN_PYPROJECT) $(JAVA_POM_FILE)
	mkdir -p target

	cp ../../../lib/java/target/*.jar target/uapi.jar
	mvn install:install-file -Dfile=target/uapi.jar -DgroupId=io.github.brenbar -DartifactId=uapi -Dversion=1.0 -Dpackaging=jar

	cp ../../../tool/uapicodegen/dist/*.tar.gz target/uapicodegen.tar.gz
	poetry lock
	poetry install
	poetry run python -m uapicodegen --schema-dir ../../test/schema/example --lang java --out src/gen/java/uapitest --package uapitest


dep:
	cd ../../../tool/uapicodegen && make
	cd ../../../lib/java && make

