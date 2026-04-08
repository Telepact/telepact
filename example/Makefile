#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

EXAMPLES := py-binary py-http-cookie-auth py-links py-select py-websocket

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
