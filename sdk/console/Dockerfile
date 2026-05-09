#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
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