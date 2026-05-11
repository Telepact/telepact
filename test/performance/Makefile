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

.PHONY: prepare prepare-py prepare-ts prepare-java run clean

prepare: prepare-py prepare-ts prepare-java

prepare-py:
$(MAKE) -C python

prepare-ts:
$(MAKE) -C typescript

prepare-java:
$(MAKE) -C java

run: prepare
uv run --project python python /home/runner/work/telepact/telepact/test/performance/runner.py

clean:
$(MAKE) -C python clean
$(MAKE) -C typescript clean
$(MAKE) -C java clean
rm -f results/*.json
