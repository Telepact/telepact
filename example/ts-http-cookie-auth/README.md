# ts-http-cookie-auth

Minimal TypeScript Telepact server that reads a session cookie at the HTTP boundary and maps it to `@auth_`.

Commands:

- `make run` — start the server on `http://127.0.0.1:8092`
- `make check` — verify both unauthenticated and authenticated requests
