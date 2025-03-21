.PHONY: all dep

all: dep
	rm -rf target
	mkdir -p target

	cp ../../../lib/java/target/*.jar target/telepact.jar
	mvn install:install-file -Dfile=target/telepact.jar -DgroupId=io.github.telepact -DartifactId=telepact -Dversion=1.0 -Dpackaging=jar

	telepact codegen --schema-dir ../../runner/schema/example --lang java --out src/gen/java/telepacttest --package telepacttest

dep:
	cd ../../../lib/java && make