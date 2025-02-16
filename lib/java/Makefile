SRC_FILES = $(shell find src -name '*.java')
POM_FILE = pom.xml

.PHONY: all

all: $(POM_FILE)
	mkdir -p src/main/resources
	cp ../../common/*.json src/main/resources
	cp ../../LICENSE ../../NOTICE src/main/resources
	mvn install

$(POM_FILE): $(SRC_FILES)
	uapi-version bump || (echo "Install uapi-version bump with 'pipx install ../../tool/uapi_version'" && exit 1)
