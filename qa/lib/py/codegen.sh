pipenv uninstall uapicodegen && pipenv --clear && pipenv lock && pipenv install ../../../tool/uapicodegen/dist/uapicodegen-0.0.1-py3-none-any.whl --clear

pipenv run python -m uapicodegen --schema ../../test/schema/example/example.uapi.json --lang py --out uapitest/gen --package uapitest