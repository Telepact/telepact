#!bin/bash

poetry export --without-hashes --format=requirements.txt -o requirements.txt
PROJECT_ROOT=$(cd ../.. && pwd)
echo $PROJECT_ROOT
sed -i "s|file://$PROJECT_ROOT/lib/py|file:///uapi/|g" requirements.txt
sed -i 's/;.*//' requirements.txt

docker build -f Dockerfile -t uapi-mock ../..