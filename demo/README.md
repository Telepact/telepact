# Telepact Demo

This directory contains a full-stack Telepact todo application built only from published Telepact artifacts:

- Browser frontend: TypeScript + React + `telepact` npm package
- Backend-for-frontend: TypeScript + Express + `telepact` npm package
- Todo service: Python + FastAPI + `telepact` PyPI package
- Planner service: Java + `io.github.telepact:telepact` from Maven Central
- Testing and mocking: `telepact-cli` from PyPI and Playwright from npm

## Layout

- `schemas/`: `.telepact.yaml` contracts for browser, todo, and planner APIs
- `apps/frontend`: browser app
- `apps/bff`: TypeScript BFF and static host
- `services/todo-python`: Python todo service
- `services/planner-java`: Java planner service
- `tests/e2e`: Playwright end-to-end tests

## Local setup

1. Install the root Node dependencies:

   ```sh
   npm install
   ```

2. Install the Python runtime and CLI into the demo-local virtual environment:

   ```sh
   python3 -m venv .venv
   ./.venv/bin/pip install telepact==1.0.0a204 telepact-cli==1.0.0a204 fastapi uvicorn httpx pytest
   ```

3. Run the services in development:

   ```sh
   npm run dev:frontend
   npm run dev:bff
   ```

   In separate terminals:

   ```sh
   cd services/todo-python
   PYTHONPATH=src ../../.venv/bin/python -m uvicorn todo_service.app:app --reload --port 7001
   ```

   ```sh
   cd services/planner-java
   mvn -q exec:java
   ```

## Tests

- Frontend:

  ```sh
  npm run test:frontend
  ```

- BFF:

  ```sh
  npm run test:bff
  ```

- Python service:

  ```sh
  cd services/todo-python
  PYTHONPATH=src ../../.venv/bin/python -m pytest
  ```

- Java service:

  ```sh
  cd services/planner-java
  mvn test
  ```

- Full-stack e2e:

  ```sh
  npm run test:e2e
  ```
