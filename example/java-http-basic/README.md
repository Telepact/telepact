# java-http-basic

Minimal Java Telepact example that runs as a one-shot JUnit test.

Test command:

```bash
make -C ../../lib/java
mvn -q -s settings.xml -Dtelepact.version=$(cat ../../VERSION.txt) test
```
