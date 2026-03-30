# ts-http-cookie-auth

Minimal TypeScript Telepact example that runs as a one-shot `node:test` suite and maps a session cookie to `@auth_` at the HTTP boundary.

Test command:

```bash
make -C ../../lib/ts
cp ../../lib/ts/dist-tgz/*.tgz telepact.tgz
npm install
npm test
```
