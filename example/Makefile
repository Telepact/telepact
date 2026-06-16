#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

EXAMPLES := full-stack full-stack-proxy py-binary py-codegen py-http-cookie-auth py-links py-select py-simple-auth py-websocket ts-binary ts-codegen ts-http-cookie-auth ts-links ts-select ts-simple-auth ts-websocket

.PHONY: list check run

list:
	@printf '%s\n' $(EXAMPLES)

check:
	@for example in $(EXAMPLES); do \
		echo "==> $$example"; \
		$(MAKE) -C $$example run || exit $$?; \
	done

run:
	@test -n "$(EXAMPLE)" || (echo "Usage: make run EXAMPLE=<name>" && exit 1)
	@$(MAKE) -C $(EXAMPLE) run
