VERSION_FILE = VERSION.txt
SRC_FILES = $(shell find uapi -name '*.py' -o -name '*.toml')
PYPROJECT_FILE = pyproject.toml
JSON_FILES = $(shell find uapi -name '*.uapi.json')
COMMON_JSON_FILES = $(shell find ../../common -name '*.uapi.json')

.PHONY: all

all: $(VERSION_FILE)

$(VERSION_FILE): $(SRC_FILES) $(JSON_FILES)
	@awk -F. '{print $$1"."$$2"."$$3+1}' $(VERSION_FILE) > $(VERSION_FILE).tmp && mv $(VERSION_FILE).tmp $(VERSION_FILE)
	@sed -i '' 's/^version = ".*"/version = \"$(shell cat $(VERSION_FILE))\"/' $(PYPROJECT_FILE)
	@echo "Version updated to $$(cat $(VERSION_FILE))"

$(JSON_FILES): $(COMMON_JSON_FILES)
	cp ../../common/*.uapi.json uapi