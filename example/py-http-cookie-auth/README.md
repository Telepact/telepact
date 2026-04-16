# py-http-cookie-auth

Minimal Python Telepact example that shows Telepact's recommended browser auth
flow:

- define a session credential in `union.Auth_`
- read the browser cookie at the HTTP boundary
- translate it into `@auth_`
- normalize it in `on_auth`

Run it:

```bash
make run
```
