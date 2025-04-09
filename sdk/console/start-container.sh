#!/bin/bash

LOG_FILE="start-container.log"

# Redirect stdout and stderr to the log file
rm -f $LOG_FILE
exec > >(tee -a $LOG_FILE) 2>&1

VERSION=$(cat ../../VERSION.txt)
CONTAINER_NAME="telepact_console"

# Function to stop and remove the container
cleanup() {
  echo "Stopping and removing container..."
  docker rm -f $CONTAINER_NAME
}

# Set trap to ensure cleanup on script exit
trap cleanup EXIT

# Run the Docker container
docker run --name $CONTAINER_NAME -p 8084:8080 -d telepact-console:$VERSION

# Wait for the parent process (e.g., Playwright) to exit
echo "Container is running. Waiting for parent process to exit..."
while ps -p $PPID > /dev/null; do
  sleep 1
done
