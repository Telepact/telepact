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

FROM nginx:alpine

COPY build/ /usr/share/nginx/html/

RUN touch /usr/share/nginx/html/override.js

EXPOSE 8080

COPY nginx.conf /etc/nginx/conf.d/nginx.conf

RUN mkdir -p /var/log/nginx && \
    mkdir -p /var/cache/nginx && \
    mkdir -p /var/run/nginx && \
    touch /var/run/nginx.pid && \
    chown -R nobody:nogroup /var/log/nginx && \
    chown -R nobody:nogroup /var/cache/nginx && \
    chown -R nobody:nogroup /var/run/nginx && \
    chown nobody:nogroup /var/run/nginx.pid

USER nobody