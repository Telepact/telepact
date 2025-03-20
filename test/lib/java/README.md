## Generating code

```
pipenv uninstall msgpactcodegen && pipenv --clear && pipenv lock && pipenv install ../../../tool/msgpactcodegen/dist/msgpactcodegen-0.0.1-py3-none-any.whl --clear

pipenv run python -m msgpactcodegen --schema ../../test/example.msgpact.json --lang java --out src/gen/java/msgpacttest --package msgpacttest
```
