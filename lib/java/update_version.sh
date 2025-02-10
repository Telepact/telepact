#!/bin/bash

# Read the version from VERSION.txt
VERSION=$(cat VERSION.txt)

# Use sed to replace the version number in pom.xml
sed -i '' -e "/<artifactId>uapi<\/artifactId>/ {
  N
  s/<version>.*<\/version>/<version>${VERSION//\//\\/}<\/version>/
}" $1