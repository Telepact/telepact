VERSION_FILE = VERSION.txt
SRC_FILES = $(shell find uapi -name '*.py' -o -name '*.toml' -o -name '*.json')
PYPROJECT_FILE = pyproject.toml

.PHONY: all

all: $(VERSION_FILE)

$(VERSION_FILE): $(SRC_FILES)
	@awk -F. '{print $$1"."$$2"."$$3+1}' $(VERSION_FILE) > $(VERSION_FILE).tmp && mv $(VERSION_FILE).tmp $(VERSION_FILE)
	@sed -i '' 's/^version = ".*"/version = \"$(shell cat $(VERSION_FILE))\"/' $(PYPROJECT_FILE)
	@echo "Version updated to $$(cat $(VERSION_FILE))"
