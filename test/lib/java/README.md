## Generating code

```
pipenv uninstall telepactcodegen && pipenv --clear && pipenv lock && pipenv install ../../../tool/telepactcodegen/dist/telepactcodegen-0.0.1-py3-none-any.whl --clear

pipenv run python -m telepactcodegen --schema ../../test/example.telepact.json --lang java --out src/gen/java/telepacttest --package telepacttest
```
