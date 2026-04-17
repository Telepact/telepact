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

FROM node:22-alpine AS console

WORKDIR /work

COPY telepact-console.tgz ./

RUN npm init -y
RUN npm install --ignore-scripts --omit=dev ./telepact-console.tgz
RUN TELEPACT_CONSOLE_ROOT="$(node --input-type=module -e 'import { selfHostedRoot } from "telepact-console/self-hosted"; process.stdout.write(selfHostedRoot)')" && \
    mkdir -p /out && \
    cp -R "$TELEPACT_CONSOLE_ROOT"/. /out/

FROM nginx:alpine

COPY --from=console /out/ /usr/share/nginx/html/
COPY override.js /usr/share/nginx/html/override.js
