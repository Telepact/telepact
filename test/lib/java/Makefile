.PHONY: all dep

all: dep
	rm -rf target
	mkdir -p target

	cp ../../../lib/java/target/*.jar target/msgpact.jar
	mvn install:install-file -Dfile=target/msgpact.jar -DgroupId=io.github.msgpact -DartifactId=msgpact -Dversion=1.0 -Dpackaging=jar

	msgpact codegen --schema-dir ../../runner/schema/example --lang java --out src/gen/java/msgpacttest --package msgpacttest

dep:
	cd ../../../lib/java && make