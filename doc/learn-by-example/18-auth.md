# 18. Auth

Let's look at Telepact's auth convention from the client's side.

## Start the demo server

```sh
telepact demo-server --port 8000
```

## Find the auth shapes

From the public schema:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.api_": {}}]'
```

The important user-defined part is:

```json
{
  "union.Auth_": [
    {"Ephemeral": {"username": "string"}},
    {"Session": {"token": "string"}}
  ]
}
```

That is our hint that auth-related behavior is part of this service's contract.

Now include internal definitions:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

Now we also see:

```json
{
  "headers.Auth_": {
    "@auth_": "union.Auth_"
  }
}
```

and:

```json
{
  "errors.Auth_": [
    {"ErrorUnauthenticated_": {"message!": "string"}},
    {"ErrorUnauthorized_": {"message!": "string"}}
  ]
}
```

## Call an auth-protected function without auth

```sh
curl -s localhost:8000/api -d '[{}, {"fn.logout": {"username": "shared"}}]'
```

```json
[{}, {"ErrorUnauthenticated_": {"message!": "Valid authentication is required."}}]
```

## Log in, then send `@auth_`

Login:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.login": {"username": "doc-user"}}]'
```

Example response:

```json
[{}, {"Ok_": {"token": "nj-tuNyu6XVA7TAtg4RWOA"}}]
```

Now use that token:

```sh
curl -s localhost:8000/api -d '[{"@auth_": {"Session": {"token": "nj-tuNyu6XVA7TAtg4RWOA"}}}, {"fn.logout": {"username": "doc-user"}}]'
```

```json
[{}, {"Ok_": {}}]
```

This login/logout pair is specific to the demo server. Other Telepact services
can choose different auth policies. The common convention is that auth travels
through `@auth_`.

Next: [19. Minimum Python client](./19-minimum-python-client.md)
