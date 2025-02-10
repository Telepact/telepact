VERSION_FILE = VERSION.txt
SRC_FILES = $(shell find src -name '*.java')
POM_FILE = pom.xml
JSON_FILES = $(shell find src/main/resources -name '*.uapi.json')
COMMON_JSON_FILES = $(shell find ../../common -name '*.uapi.json')

.PHONY: all

all: $(VERSION_FILE)

$(VERSION_FILE): $(SRC_FILES) $(JSON_FILES)
	@awk -F. '{print $$1"."$$2"."$$3+1}' $(VERSION_FILE) > $(VERSION_FILE).tmp && mv $(VERSION_FILE).tmp $(VERSION_FILE)
	@./update_version.sh $(POM_FILE)
	@echo "Version updated to $$(cat $(VERSION_FILE))"

$(JSON_FILES): $(COMMON_JSON_FILES)
	cp ../../common/*.uapi.json src/main/resources