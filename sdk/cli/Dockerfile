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

FROM python:3.11-slim

RUN pip install --no-cache-dir pipx
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

COPY tmp/telepact_cli.tar.gz telepact_cli.tar.gz

RUN pipx install telepact_cli.tar.gz

USER nobody

ENTRYPOINT ["telepact"]

CMD ["--help"]
