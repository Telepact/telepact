.PHONY: all clean

all:
	mkdir -p src/main/resources
	cp ../../common/*.json src/main/resources
	cp ../../LICENSE ../../NOTICE src/main/resources
	mvn install

clean:
	mvn clean
	rm -rf src/main/resources
	rm -rf target
