FROM maven:3.9.11-eclipse-temurin-21 AS build
WORKDIR /app

COPY services/planner-java /app/services/planner-java
RUN mvn -q -f /app/services/planner-java/pom.xml package -DskipTests

FROM eclipse-temurin:21-jre
WORKDIR /app

COPY --from=build /app/services/planner-java/target/planner-java-0.1.0.jar /app/planner-java.jar
COPY schemas /app/schemas

ENV PORT=7002
ENV SCHEMA_DIR=/app/schemas/planner
ENV TODO_SERVICE_URL=http://todo-python:7001/api

CMD ["java", "-jar", "/app/planner-java.jar"]
