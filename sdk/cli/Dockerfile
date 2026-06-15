#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

FROM python:3.11-slim

RUN pip install --no-cache-dir uv
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

COPY tmp/telepact_cli.tar.gz telepact_cli.tar.gz

RUN uv tool install telepact_cli.tar.gz

USER nobody

ENTRYPOINT ["telepact"]

CMD ["--help"]
