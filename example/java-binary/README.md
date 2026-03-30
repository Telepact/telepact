# java-binary

Minimal Java Telepact example that runs as a one-shot JUnit test and verifies binary negotiation.

Test command:

```bash
make -C ../../lib/java
mvn -q -s settings.xml -Dtelepact.version=$(cat ../../VERSION.txt) test
```
