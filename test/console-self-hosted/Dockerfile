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

COPY sdk/console/package.json /work/sdk/console/package.json
COPY sdk/console/cli.js /work/sdk/console/cli.js
COPY sdk/console/self-hosted.js /work/sdk/console/self-hosted.js
COPY sdk/console/LICENSE /work/sdk/console/LICENSE
COPY sdk/console/NOTICE /work/sdk/console/NOTICE
COPY sdk/console/build /work/sdk/console/build

RUN npm init -y
RUN npm install --ignore-scripts --omit=dev /work/sdk/console
RUN TELEPACT_CONSOLE_ROOT="$(node --input-type=module -e 'import { selfHostedRoot } from "telepact-console/self-hosted"; process.stdout.write(selfHostedRoot)')" && \
    mkdir -p /out && \
    cp -R "$TELEPACT_CONSOLE_ROOT"/. /out/

FROM nginx:alpine

COPY --from=console /out/ /usr/share/nginx/html/
COPY test/console-self-hosted/override.js /usr/share/nginx/html/override.js
