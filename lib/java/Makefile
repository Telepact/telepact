SRC_FILES = $(shell find src -name '*.java')
POM_FILE = pom.xml
JSON_FILES = $(shell find src/main/resources -name '*.uapi.json')
COMMON_JSON_FILES = $(shell find ../../common -name '*.uapi.json')

.PHONY: all

all: $(POM_FILE)

$(POM_FILE): $(SRC_FILES) $(JSON_FILES)
	bump-patch-version || (echo "Install bump-patch-version with 'pipx install ../../tool/bump_patch_version'" && exit 1)

$(JSON_FILES): $(COMMON_JSON_FILES)
	cp ../../common/*.uapi.json src/main/resources