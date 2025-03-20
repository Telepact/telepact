# Use an official Python runtime as a parent image
FROM python:3.11-slim

RUN pip install --no-cache-dir pipx
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

COPY msgpact_cli.tar.gz msgpact_cli.tar.gz

RUN pipx install msgpact_cli.tar.gz

RUN which msgpact

EXPOSE 8080

CMD ["msgpact", "mock"]
