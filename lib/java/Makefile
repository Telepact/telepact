SRC_FILES = $(shell find src -name '*.java')
POM_FILE = pom.xml
JSON_FILES = $(shell find src/main/resources -name '*.uapi.json')
COMMON_JSON_FILES = $(shell find ../../common -name '*.uapi.json')

.PHONY: all

all: $(POM_FILE)

$(POM_FILE): $(SRC_FILES) $(JSON_FILES)
	uapi-version bump || (echo "Install uapi-version bump with 'pipx install ../../tool/uapi_version'" && exit 1)
	mvn install

$(JSON_FILES): $(COMMON_JSON_FILES)
	cp ../../common/*.uapi.json src/main/resources