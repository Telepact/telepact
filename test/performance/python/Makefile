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

LIB_TAR_GZ := ../../../lib/py/dist/*.tar.gz
TAR_GZ := telepact.tar.gz

all: $(TAR_GZ)
uv sync --all-groups
uv pip install --python .venv/bin/python ./telepact.tar.gz

dep:
$(MAKE) -C ../../../lib/py

$(TAR_GZ): dep
cp $(LIB_TAR_GZ) telepact.tar.gz

run:
uv run python perf/main.py

clean:
rm -f telepact.tar.gz
rm -rf .venv
rm -f uv.lock
