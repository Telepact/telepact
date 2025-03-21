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

docker compose up --build -d
if [ $? -ne 0 ]; then
  echo "Failed to start docker compose."
  exit 1
fi

# Ensure docker-compose down runs even if there is a failure
trap 'docker-compose down' EXIT

export SERVER1=http://localhost:8081/api
export SERVER2=http://localhost:8082/api
export REQUEST='[{},{"fn.ping_":{}}]'
export EXPECTED_RESPONSE='[{}, {"Ok_": {}}]'

# Function to test server response
test_server_response() {
  local server=$1
  local response=$(curl -s -X POST -d "$REQUEST" -H "Content-Type: application/json" $server)
  if [ "$response" == "$EXPECTED_RESPONSE" ]; then
    echo "Test passed for $server"
    return 0
  else
    echo "Test failed for $server"
    echo "Expected: $EXPECTED_RESPONSE"
    echo "Got: $response"
    return 1
  fi
}

# Retry logic for server startup
retry_test_server_response() {
  local server=$1
  local retries=15
  local count=0
  local result=2
  local host=$(echo $server | awk -F[/:] '{print $4}')
  local port=$(echo $server | awk -F[/:] '{print $5}')
  until [ $result -eq 0 ] || [ $count -eq $retries ]; do
    if nc -z $host $port; then
      test_server_response $server
      result=$?
    else
      echo "Server $server is not reachable. Retrying... ($((++count))/$retries)"
    fi
    if [ $result -ne 0 ]; then
      sleep 1
    fi
  done
  if [ $result -eq 2 ]; then
    echo "Failed to connect to $server after $retries retries."
  fi
  return $result
}

# Test each server with retry logic in parallel
retry_test_server_response $SERVER1 &
pid1=$!
retry_test_server_response $SERVER2 &
pid2=$!

# Wait for both tests to complete
wait $pid1
result1=$?
wait $pid2
result2=$?

# Check if any test failed
if [ $result1 -ne 0 ] || [ $result2 -ne 0 ]; then
  echo "One or more tests failed."
  exit 1
else
  echo "All tests passed."
  exit 0
fi

# docker-compose down will be called automatically by the trap
