FROM node:22-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:22-alpine
WORKDIR /app

COPY package*.json ./
RUN npm ci --omit=dev

COPY --from=build /app/apps/bff/dist /app/apps/bff/dist
COPY --from=build /app/apps/bff/static /app/apps/bff/static
COPY --from=build /app/schemas /app/schemas

ENV PORT=3000
ENV TODO_SERVICE_URL=http://todo-python:7001/api
ENV PLANNER_SERVICE_URL=http://planner-java:7002/api

CMD ["node", "apps/bff/dist/server.js"]
