# Use an official Python runtime as a parent image
FROM python:3.11-slim

RUN pip install --no-cache-dir pipx
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

COPY telepact_cli.tar.gz telepact_cli.tar.gz

RUN pipx install telepact_cli.tar.gz

RUN which telepact

EXPOSE 8080

CMD ["telepact", "mock"]
