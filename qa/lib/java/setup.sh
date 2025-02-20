#!/bin/bash

# Set environment variables
export NATS_URL=$1
unset VIRTUAL_ENV

make

mvn verify -q -B
