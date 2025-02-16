SRC_FILES = $(shell find src -name '*.java')
POM_FILE = pom.xml
JSON_FILES = $(shell find src/main/resources -name '*.json')
COMMON_JSON_FILES = $(shell find ../../common -name '*.json')

.PHONY: all

all: $(POM_FILE)
	mvn install

$(POM_FILE): $(SRC_FILES) $(JSON_FILES)
	uapi-version bump || (echo "Install uapi-version bump with 'pipx install ../../tool/uapi_version'" && exit 1)

$(JSON_FILES): $(COMMON_JSON_FILES)
	mkdir -p src/main/resources
	cp ../../common/*.json src/main/resources
	mkdir -p target/META-INF
	cp ../../LICENSE ../../NOTICE target/META-INF
