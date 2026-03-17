FROM python:3.13-slim
WORKDIR /app

COPY services/todo-python /app/services/todo-python
COPY schemas /app/schemas

RUN pip install --no-cache-dir /app/services/todo-python

WORKDIR /app/services/todo-python

ENV PORT=7001
ENV SCHEMA_DIR=/app/schemas/todo
ENV PLANNER_SERVICE_URL=http://planner-java:7002/api

CMD ["python", "-m", "uvicorn", "todo_service.app:app", "--host", "0.0.0.0", "--port", "7001"]
