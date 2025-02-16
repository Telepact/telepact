#!/bin/bash

# Set environment variables
export NATS_URL=$1
unset VIRTUAL_ENV

# Run Maven install in the target path
(cd ../../../lib/java && mvn install)

make

mvn verify
