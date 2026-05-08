# Learn by Example

Let's learn Telepact the same way we'll use it in real life: by making small,
concrete requests and watching the schema explain what is happening.

## Order

### Getting started

1. [00. Installation](#00-installation)
2. [01. Ping](#01-ping)
3. [02. Schema and `fn.add`](#02-schema-and-fn-add)
4. [03. Data type validation](#03-data-type-validation)

### Schema

5. [04. Scalar types](#04-scalar-types)
6. [05. Collection types](#05-collection-types)
7. [06. Structs](#06-structs)
8. [07. Unions](#07-unions)
9. [08. Functions](#08-functions)
10. [09. Service errors](#09-service-errors)
11. [10. Headers](#10-headers)
12. [11. Comments](#11-comments)

### Opt-in features

13. [12. Select](#12-select)
14. [13. Binary](#13-binary)

### Mocking an integration

15. [14. Mock server](#14-mock-server)
16. [15. Stock mock](#15-stock-mock)
17. [16. Stubs](#16-stubs)
18. [17. Verify](#17-verify)

### Auth

19. [18. Auth](#18-auth)

### Using Telepact client library code

20. [19. Minimum Python client](#19-minimum-python-client)
21. [20. Automatic binary negotiation](#20-automatic-binary-negotiation)

### Code generation

22. [21. Code generation](#21-code-generation)

### Running our own server

23. [22. Minimum server](#22-minimum-server)
24. [23. Logging](#23-logging)
25. [24. Server auth](#24-server-auth)
26. [25. Managed auth](#25-managed-auth)
27. [26. Schema evolution](#26-schema-evolution)
28. [27. TDD with TestClient](#27-tdd-with-testclient)
29. [28. Best practices for server implementers](#28-best-practices-for-server-implementers)

Next: [00. Installation](#00-installation)

## 00. Installation

Let's get the few tools we need for the whole walkthrough.

### Install the Telepact CLI

```sh
uv tool install --prerelease=allow telepact-cli
```

### Install the Python library

We'll use this later for the client and server examples.

```sh
pip install --pre telepact requests
```

### Check that everything is ready

```sh
telepact --help
python --version
curl --version
```

From here on, we'll assume:

- `telepact` is on our `PATH`
- `python` is available
- `curl` is available
- we are free to create small scratch files in our own working directory

Next: [01. Ping](#01-ping)

## 01. Ping

Let's start with the smallest possible Telepact conversation.

### Start the demo server

In one terminal:

```sh
telepact demo-server --port 8000
```

### Call `fn.ping_`

In another terminal:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.ping_": {}}]'
```

Response:

```json
[{}, {"Ok_": {}}]
```

### The anatomy of a Telepact message

That request was a JSON array with exactly two elements:

```json
[
  {},
  {"fn.ping_": {}}
]
```

- the first object is the **header**
- the second object is the **body**

And the response has the same shape:

```json
[
  {},
  {"Ok_": {}}
]
```

So right away, Telepact gives us a steady mental model:

1. header object
2. body object

We'll keep using that same two-object envelope all the way through the tutorial.

Next: [02. Schema and `fn.add`](#02-schema-and-fn-add)

## 02. Schema and fn.add

Now let's ask the server to describe itself.

### Start the demo server

```sh
telepact demo-server --port 8000
```

### Call `fn.api_`

```sh
curl -s localhost:8000/api -d '[{}, {"fn.api_": {}}]'
```

The response is large, so let's focus on the part that matters for `fn.add`:

```json
[
  {},
  {
    "Ok_": {
      "api": [
        ...,
        {
          "///": "A function that adds two numbers.",
          "fn.add": {
            "x": "number",
            "y": "number"
          },
          "->": [
            {
              "Ok_": {
                "result": "number"
              }
            }
          ]
        },
        ...
      ]
    }
  }
]
```

This schema is the whole interface surface area of the server. If we can read the
schema, we can discover the API without guessing.

### Call `fn.add`

Request:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.add": {"x": 1, "y": 2}}]'
```

Response:

```json
[{}, {"Ok_": {"result": 3}}]
```

### Internal names end with `_`

This is a good moment to notice a naming pattern:

- `fn.ping_` and `fn.api_` end with `_`, so they are **internal**
- `fn.add` does not end with `_`, so it was defined by the service author

Every Telepact server comes with stock internal definitions like `fn.ping_` and
`fn.api_`. Service authors add their own public definitions beside them.

If we want to see the internal definitions too, we can ask for them:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

Next: [03. Data type validation](#03-data-type-validation)

## 03. Data type validation

Let's look at one of Telepact's biggest promises: predictable validation.

### Start the demo server

```sh
telepact demo-server --port 8000
```

### Find `fn.saveVariable` in the schema

```sh
curl -s localhost:8000/api -d '[{}, {"fn.api_": {}}]'
```

The part we care about looks like this:

```json
{
  "fn.saveVariable": {
    "name": "string",
    "value": "number"
  },
  "->": [
    {
      "Ok_": {}
    }
  ]
}
```

Here, `name` and `value` are **fields**:

- they are lowercase
- they are not qualified with a prefix like `fn.` or `struct.`

And their values are **type expressions**:

- `string`
- `number`

### Send the wrong types

```sh
curl -s localhost:8000/api -d '[{}, {"fn.saveVariable": {"name": 123, "value": "oops"}}]'
```

Response:

```json
[
  {},
  {
    "ErrorInvalidRequestBody_": {
      "cases": [
        {
          "path": ["fn.saveVariable", "name"],
          "reason": {
            "TypeUnexpected": {
              "actual": {"Number": {}},
              "expected": {"String": {}}
            }
          }
        },
        {
          "path": ["fn.saveVariable", "value"],
          "reason": {
            "TypeUnexpected": {
              "actual": {"String": {}},
              "expected": {"Number": {}}
            }
          }
        }
      ]
    }
  }
]
```

This validation comes for free. Telepact servers always do it, which means
clients can trust the pattern.

We *could* learn a service by trial and error like this, but now we're ready for
the nicer path: learning to read the schema directly.

Next: [04. Scalar types](#04-scalar-types)

## 04. Scalar types

Let's start reading the schema in smaller pieces.

### Start the demo server

```sh
telepact demo-server --port 8000
```

### The scalar type expressions

| Type expression | Meaning |
| --- | --- |
| `boolean` | `true` or `false` |
| `integer` | whole number |
| `number` | JSON number |
| `string` | JSON string |
| `bytes` | binary data |

Nullability is written with a `?` suffix, like `number?` or `string?`.

### Where they show up in the demo schema

```json
{
  "fn.add": {"x": "number", "y": "number"},
  "fn.getPaperTape": {"limit!": "integer"},
  "fn.login": {"username": "string"},
  "struct.Evaluation": {
    "result": "number?",
    "timestamp": "integer",
    "successful": "boolean"
  },
  "fn.export": {},
  "->": [{"Ok_": {"blob": "bytes"}}]
}
```

### Real examples

#### `number`

```sh
curl -s localhost:8000/api -d '[{}, {"fn.add": {"x": 1.5, "y": 2}}]'
```

```json
[{}, {"Ok_": {"result": 3.5}}]
```

#### `integer`, `boolean`, and nullable `number?`

Let's create one evaluation and then read it back:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.evaluate": {"expression": {"Constant": {"value": 7}}}}]'
curl -s localhost:8000/api -d '[{}, {"fn.getPaperTape": {"limit!": 1}}]'
```

Example response:

```json
[
  {},
  {
    "Ok_": {
      "tape": [
        {
          "expression": {"Constant": {"value": 7}},
          "result": 7,
          "timestamp": 1744221600,
          "successful": true
        }
      ]
    }
  }
]
```

#### `bytes`

```sh
curl -s localhost:8000/api -d '[{}, {"fn.export": {}}]'
```

Example response:

```json
[
  {
    "@base64_": {
      "Ok_": {
        "blob": true
      }
    }
  },
  {
    "Ok_": {
      "blob": "gql2YXJpYWJsZXO..."
    }
  }
]
```

The schema says `bytes`, but JSON has no raw bytes type, so Telepact coerces the
wire value to Base64.

Next: [05. Collection types](#05-collection-types)

## 05. Collection types

Now let's add the two collection forms.

### Start the demo server

```sh
telepact demo-server --port 8000
```

### The collection type expressions

| Type expression | Meaning |
| --- | --- |
| `["string"]` | array of strings |
| `{"string": "number"}` | object whose keys are strings and whose values are numbers |

That object key is always `string`, because JSON object keys are strings.

### Where they show up in the demo schema

```json
{
  "fn.deleteVariables": {
    "names": ["string"]
  },
  "fn.saveVariables": {
    "variables": {"string": "number"}
  }
}
```

### Real examples

#### Array

```sh
curl -s localhost:8000/api -d '[{}, {"fn.deleteVariables": {"names": ["a", "b"]}}]'
```

```json
[{}, {"Ok_": {}}]
```

#### Object

```sh
curl -s localhost:8000/api -d '[{}, {"fn.saveVariables": {"variables": {"a": 2, "b": 4}}}]'
```

```json
[{}, {"Ok_": {}}]
```

#### Empty collections are already expressive

Both of these are still valid:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.deleteVariables": {"names": []}}]'
curl -s localhost:8000/api -d '[{}, {"fn.saveVariables": {"variables": {}}}]'
```

That is why Telepact does not try to express nullable collections like `[]?` or
`{}?`. Emptiness already has a natural representation.

Next: [06. Structs](#06-structs)

## 06. Structs

A struct is a product type: one JSON object with a fixed set of fields.

### Start the demo server

```sh
telepact demo-server --port 8000
```

### Look at `struct.Variable`

```json
{
  "struct.Variable": {
    "name": "string",
    "value": "number"
  }
}
```

The lowercase keys `name` and `value` are the fields.

Now let's see where that struct is reused:

```json
{
  "fn.getVariable": {
    "name": "string"
  },
  "->": [
    {
      "Ok_": {
        "variable!": "struct.Variable"
      }
    }
  ]
}
```

### Save a variable, then read it back

```sh
curl -s localhost:8000/api -d '[{}, {"fn.saveVariable": {"name": "x", "value": 3}}]'
curl -s localhost:8000/api -d '[{}, {"fn.getVariable": {"name": "x"}}]'
```

Response:

```json
[{}, {"Ok_": {"variable!": {"name": "x", "value": 3}}}]
```

### Optional fields use `!`

That `variable!` field is optional. If the variable is missing, the field is
simply omitted on the wire:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.getVariable": {"name": "missing"}}]'
```

```json
[{}, {"Ok_": {}}]
```

So in Telepact:

- fields are required by default
- `!` means the field is optional and may be omitted entirely

Next: [07. Unions](#07-unions)

## 07. Unions

A union is a tagged choice. Exactly one tag shows up at a time.

### Start the demo server

```sh
telepact demo-server --port 8000
```

### Look at `union.Expression`

```json
{
  "union.Expression": [
    {"Constant": {"value": "number"}},
    {"Variable": {"name": "string"}},
    {"Add": {"left": "union.Expression", "right": "union.Expression"}},
    {"Sub": {"left": "union.Expression", "right": "union.Expression"}},
    {"Mul": {"left": "union.Expression", "right": "union.Expression"}},
    {"Div": {"left": "union.Expression", "right": "union.Expression"}}
  ]
}
```

Uppercase keys are the tags. Inside each tag, lowercase keys are fields again.

Now let's see where that union is used:

```json
{
  "struct.Evaluation": {
    "expression": "union.Expression",
    "result": "number?",
    "timestamp": "integer",
    "successful": "boolean"
  }
}
```

And `struct.Evaluation` is returned by `fn.getPaperTape`.

### Make one union value, then read it back

```sh
curl -s localhost:8000/api -d '[{}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 2}}, "right": {"Constant": {"value": 3}}}}}}]'
curl -s localhost:8000/api -d '[{}, {"fn.getPaperTape": {"limit!": 1}}]'
```

Example response:

```json
[
  {},
  {
    "Ok_": {
      "tape": [
        {
          "expression": {
            "Add": {
              "left": {"Constant": {"value": 2}},
              "right": {"Constant": {"value": 3}}
            }
          },
          "result": 5,
          "timestamp": 1744221600,
          "successful": true
        }
      ]
    }
  }
]
```

Only one tag appears in that instance of `union.Expression`: `Add`.

Next: [08. Functions](#08-functions)

## 08. Functions

In Telepact, a function is an argument struct plus a result union.

### Start the demo server

```sh
telepact demo-server --port 8000
```

### Read a function definition

Here is `fn.evaluate`:

```json
{
  "fn.evaluate": {
    "expression": "union.Expression"
  },
  "->": [
    {
      "Ok_": {
        "result": "number",
        "saveResult": "fn.saveVariable"
      }
    },
    {
      "ErrorUnknownVariables": {
        "unknownVariables": ["string"]
      }
    },
    {
      "ErrorCannotDivideByZero": {}
    }
  ]
}
```

The function entrypoint itself defines the argument struct. The `->` entrypoint
defines the result union.

`Ok_` is always required. Everything else is treated as an error result.

### Links

Notice `saveResult` uses `fn.saveVariable` as a type expression. That is a link:
the server is returning a prepopulated future call shape.

Let's see it:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 2}}, "right": {"Constant": {"value": 4}}}}}}]'
```

```json
[
  {},
  {
    "Ok_": {
      "result": 6,
      "saveResult": {
        "fn.saveVariable": {
          "name": "result",
          "value": 6
        }
      }
    }
  }
]
```

### Error cases

Unknown variable:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.evaluate": {"expression": {"Variable": {"name": "missing"}}}}]'
```

```json
[{}, {"ErrorUnknownVariables": {"unknownVariables": ["missing"]}}]
```

Divide by zero:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.evaluate": {"expression": {"Div": {"left": {"Constant": {"value": 4}}, "right": {"Constant": {"value": 0}}}}}}]'
```

```json
[{}, {"ErrorCannotDivideByZero": {}}]
```

### Optional fields in function-shaped definitions

Optional fields still use `!`, even inside function arguments:

```json
{
  "fn.getPaperTape": {
    "limit!": "integer"
  }
}
```

So both of these are valid:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.getPaperTape": {}}]'
curl -s localhost:8000/api -d '[{}, {"fn.getPaperTape": {"limit!": 1}}]'
```

Next: [09. Service errors](#09-service-errors)

## 09. Service errors

Some errors belong to one function. Others can happen anywhere in a service.

### Start the demo server

```sh
telepact demo-server --port 8000
```

### Look at `errors.Availability`

```json
{
  "errors.Availability": [
    {
      "ErrorUnavailable": {}
    }
  ]
}
```

This shape looks just like a union definition, but it behaves differently:
everything declared here is added to every service function.

That is why `ErrorUnavailable` can appear broadly across the demo service.

### What service errors are for

This kind of definition is for service-wide concerns, like availability.

It is **not** the place for placeholder errors like:

- "404 Not Found"
- "400 Bad Request"

Telepact steers us away from both:

- for "not found", prefer expressive data like an optional field, as in
  `fn.getVariable`
- for request-shape problems, Telepact already gives us built-in validation
  errors like `ErrorInvalidRequestBody_`
- for business-rule failures, define function-specific errors like
  `ErrorCannotDivideByZero`

Next: [10. Headers](#10-headers)

## 10. Headers

Headers are shaped a bit like structs, but they play by different rules.

### Start the demo server

```sh
telepact demo-server --port 8000
```

### Look at internal header definitions

```sh
curl -s localhost:8000/api -d '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

For example:

```json
{
  "headers.Id_": {
    "@id_": "any"
  },
  "->": {
    "@id_": "any"
  }
}
```

Headers differ from structs in two important ways:

1. every defined header field is already optional
2. undefined header fields are still allowed

That is why header names use `@` and do not use `!`.

### A real example with `@id_`

```sh
curl -s localhost:8000/api -d '[{"@id_": "lesson-10"}, {"fn.add": {"x": 1, "y": 2}}]'
```

Response:

```json
[{"@id_": "lesson-10"}, {"Ok_": {"result": 3}}]
```

So `@id_` is just a correlation helper: the server reflects it back.

Next: [11. Comments](#11-comments)

## 11. Comments

Telepact schemas can carry comments directly inside the schema entries.

### Start the demo server

```sh
telepact demo-server --port 8000
```

### Look for `///`

When we call `fn.api_`, we see entries like this:

```json
{
  "///": "A function that adds two numbers.",
  "fn.add": {
    "x": "number",
    "y": "number"
  },
  "->": [
    {
      "Ok_": {
        "result": "number"
      }
    }
  ]
}
```

That `///` key is just a comment. Any struct-like definition can have one:

- `fn.*`
- `struct.*`
- `union.*`
- `headers.*`
- `errors.*`

These comments are informational only. They help people and tools, but they do
not change request or response behavior.

Next: [12. Select](#12-select)

## 12. Select

Now let's turn on our first opt-in feature: field selection.

### Start the demo server

```sh
telepact demo-server --port 8000
```

### Find the internal `@select_` header

```sh
curl -s localhost:8000/api -d '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

The schema entry looks like this:

```json
{
  "headers.Select_": {
    "@select_": "_ext.Select_"
  },
  "->": {}
}
```

For the full rule set, see the
[`_ext.Select_` guide](concepts.md#ext-select).

### Compare a full response with a selected response

Full response:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 2}}, "right": {"Constant": {"value": 3}}}}}}]'
```

```json
[{}, {"Ok_": {"result": 5, "saveResult": {"fn.saveVariable": {"name": "result", "value": 5}}}}]
```

Selected response:

```sh
curl -s localhost:8000/api -d '[{"@select_": {"->": {"Ok_": ["result"]}}}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 2}}, "right": {"Constant": {"value": 3}}}}}}]'
```

```json
[{}, {"Ok_": {"result": 5}}]
```

Nothing about the function changed. We just told the server which response fields
we wanted back.

`@select_` always uses the same shape:

- `->` selects fields on the active result union
- `struct.*` selects fields on reachable structs
- `union.*` selects fields for reachable union tags

Next: [13. Binary](#13-binary)

## 13. Binary

Telepact can switch the whole message envelope into a compact binary form.
The nice part is that it is **opt-in at runtime**: the client asks for binary,
the server negotiates a field map once, and the steady-state payload gets much
smaller.

### Start the demo server

```sh
telepact demo-server --port 8000
```

### Seed a little data

```sh
curl -s localhost:8000/api -d '[{}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 2}}, "right": {"Constant": {"value": 3}}}}}}]'
curl -s localhost:8000/api -d '[{}, {"fn.evaluate": {"expression": {"Variable": {"name": "x"}}}}]'
```

### The function we are calling

```yaml
- fn.getPaperTape:
    limit!: integer
  ->:
    - Ok_:
        tape: [struct.Evaluation]
```

### Visualize the negotiation

| Step | Request header | What comes back | Size from one run |
| --- | --- | --- | --- |
| Plain JSON | none | readable JSON | 289 B |
| First binary response | `"@bin_": []` | binary body + `@enc_` map | 527 B |
| Negotiated binary response | `"@bin_": [900069279]` | compact binary body only | 72 B |

The first binary response is bigger because the server has to teach us the
encoding map. After that, the checksum in `@bin_` is enough.

### 1. Plain JSON baseline

Request body:

```json
[{}, {"fn.getPaperTape": {}}]
```

Run it:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.getPaperTape": {}}]' > /tmp/papertape-plain.json
wc -c < /tmp/papertape-plain.json
cat /tmp/papertape-plain.json
```

On one run:

```text
289
[{}, {"Ok_": {"tape": [{"expression": {"Variable": {"name": "x"}}, "result": 0.0, "timestamp": 1776277463, "successful": false}, {"expression": {"Add": {"left": {"Constant": {"value": 2}}, "right": {"Constant": {"value": 3}}}}, "result": 5, "timestamp": 1776277463, "successful": true}]}}]
```

### 2. Ask for binary

First binary request body:

```json
[{"@bin_": []}, {"fn.getPaperTape": {}}]
```

Run it:

```sh
curl -s localhost:8000/api -d '[{"@bin_": []}, {"fn.getPaperTape": {}}]' > /tmp/papertape-first.bin
wc -c < /tmp/papertape-first.bin
python - <<'PY'
from pathlib import Path
# Show non-UTF-8 bytes as replacement characters so the payload stays printable.
print(Path('/tmp/papertape-first.bin').read_bytes().decode('utf-8', 'replace'))
PY
```

On one run, the response looked like this:

```text
527
���@enc_�·,�Add·�Constant·�Div·�Mul·�Ok_·�Sub·�Variable·�api·�blob·�expression�fn.add
�fn.api_·�fn.deleteVariable·�fn.deleteVariables·�fn.evaluate·�fn.export·�fn.getPaperTape·�fn.getVariable·�fn.getVariables·�fn.import·�fn.login·�fn.logout·�fn.ping_·�fn.saveVariable·�fn.saveVariables·�includeExamples!·�includeInternal!·�left·�limit!·�name·�names·�result·�right �saveResult!�successful"�tape#�timestamp$�token%�username&�value'�variable!(�variables)�x*�y+�@bin_��5����·�#���·�·�x·�········$�i���"·�·�·�·�'· �·�'···$�i���"�
```

That noisy `@enc_` section is the one-time negotiation payload.

### 3. Reuse the negotiated checksum

Extract the checksum that came back in `@bin_`:

```sh
checksum=$(uv run --with msgpack python - <<'PY'
import msgpack
with open('/tmp/papertape-first.bin', 'rb') as f:
    data = msgpack.unpackb(f.read(), raw=False, strict_map_key=False)
print(data[0]['@bin_'][0])
PY
)
echo "$checksum"
```

On one run:

```text
900069279
```

Now send that checksum back:

```json
[{"@bin_": [900069279]}, {"fn.getPaperTape": {}}]
```

```sh
curl -s localhost:8000/api -d "[{\"@bin_\": [$checksum]}, {\"fn.getPaperTape\": {}}]" > /tmp/papertape-steady.bin
wc -c < /tmp/papertape-steady.bin
python - <<'PY'
from pathlib import Path
# Show non-UTF-8 bytes as replacement characters so the payload stays printable.
print(Path('/tmp/papertape-steady.bin').read_bytes().decode('utf-8', 'replace'))
PY
```

On one run, the negotiated binary response dropped to:

```text
72
���@bin_��5����·�#���·�·�x·�········$�i���"·�·�·�·�'· �·�'···$�i���"�
```

That is the win: the payload shrank from 289 B of JSON to 72 B of negotiated
binary, while still representing the same response.

Under the hood, this binary format is powered by [MessagePack](https://msgpack.org/).

In normal client code, we should not handcraft `@bin_` like this. A Telepact
runtime client can do the negotiation and caching for us automatically.

Next: [14. Mock server](#14-mock-server)

## 14. Mock server

Now let's move from "calling a service" to "integrating with a service."

### Start the live demo server

```sh
telepact demo-server --port 8000
```

### Start a mock server from the live schema

In a second terminal:

```sh
telepact mock --http-url http://localhost:8000/api --port 8001 --path /api
```

The mock server absorbs the live server's schema, which makes it a great
integration partner while we are building a client.

### The normal integration pattern

This should be our default habit:

1. point a mock at the live Telepact server
2. develop against the mock first
3. switch to the live service later

If we want a cached local copy of the schema, we can also do this:

```sh
telepact fetch --http-url http://localhost:8000/api --output-dir ./cached-schema
telepact mock --dir ./cached-schema --port 8001 --path /api
```

### Compare the public schema

Live server:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.api_": {}}]'
```

Mock server:

```sh
curl -s localhost:8001/api -d '[{}, {"fn.api_": {}}]'
```

Those public schemas match.

If we include internal definitions on the mock, we see more:

```sh
curl -s localhost:8001/api -d '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

That extra surface is the mock's control plane.

Next: [15. Stock mock](#15-stock-mock)

## 15. Stock mock

Before we configure anything, let's see what the mock already gives us.

### Start the live demo server

```sh
telepact demo-server --port 8000
```

### Start the mock server

```sh
telepact mock --http-url http://localhost:8000/api --port 8001 --path /api
```

### A malformed request still fails correctly

```sh
curl -s localhost:8001/api -d '[{}, {"fn.add": {"x": "oops", "y": 2}}]'
```

```json
[{}, {"ErrorInvalidRequestBody_": {"cases": [{"path": ["fn.add", "x"], "reason": {"TypeUnexpected": {"actual": {"String": {}}, "expected": {"Number": {}}}}}]}}]
```

That is already powerful: our integration code can prove it is sending
schema-correct requests before it ever talks to the real service.

### A valid request gets a type-correct nonsense result

```sh
curl -s localhost:8001/api -d '[{}, {"fn.add": {"x": 1, "y": 2}}]'
```

Example response:

```json
[{}, {"Ok_": {"result": 0.001007557381413671}}]
```

The exact value will vary, but the important part is stable:

- the request is validated
- the response is type compliant

If we need specific values, we'll add stubs next.

Next: [16. Stubs](#16-stubs)

## 16. Stubs

Stock mock data is great for shape checking. Stubs are how we ask for specific
results.

### Start the live demo server

```sh
telepact demo-server --port 8000
```

### Start the mock server

```sh
telepact mock --http-url http://localhost:8000/api --port 8001 --path /api
```

### Find `fn.createStub_`

```sh
curl -s localhost:8001/api -d '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

The key entry is:

```json
{
  "fn.createStub_": {
    "stub": "_ext.Stub_",
    "strictMatch!": "boolean",
    "count!": "integer"
  }
}
```

For the `_ext.Stub_` shape, see the
[mock extensions guide](concepts.md#mock-extensions).

### Create a stub for `fn.add`

```sh
curl -s localhost:8001/api -d '[{}, {"fn.createStub_": {"stub": {"fn.add": {"x": 1, "y": 2}, "->": {"Ok_": {"result": 99}}}}}]'
```

```json
[{}, {"Ok_": {}}]
```

Now the matching call returns our chosen result:

```sh
curl -s localhost:8001/api -d '[{}, {"fn.add": {"x": 1, "y": 2}}]'
```

```json
[{}, {"Ok_": {"result": 99}}]
```

The mock has many more knobs for strictness, randomness, and generation policy.
When we want to reset stubs, the lifecycle function is there too:

```sh
curl -s localhost:8001/api -d '[{}, {"fn.clearStubs_": {}}]'
```

Next: [17. Verify](#17-verify)

## 17. Verify

Sometimes we do not need to control the response. We just need to prove that our
client made a call.

### Start the live demo server

```sh
telepact demo-server --port 8000
```

### Start the mock server

```sh
telepact mock --http-url http://localhost:8000/api --port 8001 --path /api
```

### Find `fn.verify_`

```sh
curl -s localhost:8001/api -d '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

The entry looks like this:

```json
{
  "fn.verify_": {
    "call": "_ext.Call_",
    "strictMatch!": "boolean",
    "count!": "union.CallCountCriteria_"
  }
}
```

For the `_ext.Call_` shape, see the
[mock extensions guide](concepts.md#mock-extensions).

### Verify before the call

Let's clear any old history first:

```sh
curl -s localhost:8001/api -d '[{}, {"fn.clearCalls_": {}}]'
curl -s localhost:8001/api -d '[{}, {"fn.verify_": {"call": {"fn.add": {"x": 7, "y": 8}}}}]'
```

Response:

```json
[{}, {"ErrorVerificationFailure": {"reason": {"TooFewMatchingCalls": {"wanted": {"AtLeast": {"times": 1}}, "found": 0, "allCalls": []}}}}]
```

### Verify after the call

```sh
curl -s localhost:8001/api -d '[{}, {"fn.add": {"x": 7, "y": 8}}]'
curl -s localhost:8001/api -d '[{}, {"fn.verify_": {"call": {"fn.add": {"x": 7, "y": 8}}}}]'
```

Response:

```json
[{}, {"Ok_": {}}]
```

So `fn.verify_` is our way to confirm that our side of the integration reached
out when we expected it to.

Next: [18. Auth](#18-auth)

## 18. Auth

Let's look at Telepact's auth convention from the client's side.

For the full Telepact auth boundary, including transport extraction, `onAuth`
normalization, browser cookies, and service-to-service credentials, see
the [Auth Guide](concepts.md#auth-guide).

### Start the demo server

```sh
telepact demo-server --port 8000
```

### Find the auth shapes

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

### Call an auth-protected function without auth

```sh
curl -s localhost:8000/api -d '[{}, {"fn.logout": {"username": "shared"}}]'
```

```json
[{}, {"ErrorUnauthenticated_": {"message!": "Valid authentication is required."}}]
```

### Log in, then send `@auth_`

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
can choose different auth policies. The common convention is that caller
credentials travel through `@auth_`, with `union.Auth_` as the canonical public
schema shape.

Next: [19. Minimum Python client](#19-minimum-python-client)

## 19. Minimum Python client

Now let's stop hand-writing JSON and let the Telepact Python library help us.

### Start the demo server

```sh
telepact demo-server --port 8000
```

### Install what this example needs

```sh
pip install --pre telepact requests
```

### Write a minimum client

```py
import asyncio
import requests

from telepact import Client, Message, Serializer


async def adapter(message: Message, serializer: Serializer) -> Message:
    request_bytes = serializer.serialize(message)
    response = requests.post('http://localhost:8000/api', data=request_bytes, timeout=5)
    return serializer.deserialize(response.content)


async def main() -> None:
    client = Client(adapter, Client.Options())

    await client.request(Message({}, {'fn.saveVariable': {'name': 'x', 'value': 5}}))
    response = await client.request(Message({}, {'fn.export': {}}))

    blob = response.body['Ok_']['blob']
    print(type(blob).__name__)
    print(len(blob))
    print(blob[:8].hex())


asyncio.run(main())
```

Run it:

```sh
python client.py
```

Example output:

```text
bytes
293
82a9766172696162
```

The important part is that `blob` is already Python `bytes`. We did not manually
JSON-encode the message, and we did not manually Base64-decode the wire value.

Next: [20. Automatic binary negotiation](#20-automatic-binary-negotiation)

## 20. Automatic binary negotiation

Earlier we negotiated binary by hand. Now let's let the Python client do it.

### Start the demo server

```sh
telepact demo-server --port 8000
```

### Install what this example needs

```sh
pip install --pre telepact requests
```

### Write a binary-enabled client

```py
import asyncio
import requests

from telepact import Client, Message, Serializer


async def main() -> None:
    calls = []

    async def adapter(message: Message, serializer: Serializer) -> Message:
        request_bytes = serializer.serialize(message)
        response = requests.post('http://localhost:8000/api', data=request_bytes, timeout=5)
        decoded = serializer.deserialize(response.content)
        calls.append({
            'request_headers': dict(message.headers),
            'request_len': len(request_bytes),
            'response_headers': dict(decoded.headers),
            'response_len': len(response.content),
        })
        return decoded

    options = Client.Options()
    options.use_binary = True
    options.always_send_json = False

    client = Client(adapter, options)

    for _ in range(2):
        await client.request(Message({}, {'fn.getVariables': {}}))

    for index, call in enumerate(calls, start=1):
        print(f'call {index}: {call}')


asyncio.run(main())
```

Run it:

```sh
python client.py
```

Example output:

```text
call 1: {'request_headers': {'@time_': 5000, '@bin_': []}, 'request_len': 56, 'response_headers': {'@enc_': {...}, '@bin_': [900069279]}, 'response_len': 480}
call 2: {'request_headers': {'@time_': 5000, '@bin_': [900069279]}, 'request_len': 27, 'response_headers': {'@bin_': [900069279]}, 'response_len': 25}
```

Three nice things happened for us:

1. the client automatically started the binary handshake
2. it cached the negotiated checksum and reused it
3. it sent `@time_` for us so the server can understand the client's timeout

This is the normal way to use binary with Telepact. If the schema changes, the
runtime client can re-negotiate instead of forcing us through a codegen ABI
pipeline.

Next: [21. Code generation](#21-code-generation)

## 21. Code generation

Telepact also lets us generate bindings straight from a running service.

This is an optional ergonomic upgrade. Many integrations can stop at the
runtime client plus a schema-backed mock server, which already gives strong
confidence that requests and responses are valid. Reach for code generation when
you want stronger compile-time feedback and a more SDK-like application API.

### Start the demo server

```sh
telepact demo-server --port 8000
```

### Generate Python bindings

```sh
mkdir -p ./gen
telepact codegen --schema-http-url http://localhost:8000/api --lang py --out ./gen
```

That creates Python code from the live schema. No server-managed artifact bundle
is needed; we simply point the generator at the service we want to integrate
with.

### Generated code still uses the Telepact Python library

Install the runtime:

```sh
pip install --pre telepact requests
```

### Use the generated bindings

```py
import asyncio
import requests

from telepact import Client, Message, Serializer
from gen.gen_types import TypedClient, add


async def adapter(message: Message, serializer: Serializer) -> Message:
    request_bytes = serializer.serialize(message)
    response = requests.post('http://localhost:8000/api', data=request_bytes, timeout=5)
    return serializer.deserialize(response.content)


async def main() -> None:
    raw_client = Client(adapter, Client.Options())
    client = TypedClient(raw_client)

    response = await client.add({}, add.Input.from_(x=2, y=3))
    print(response.body.pseudo_json)


asyncio.run(main())
```

Example output:

```text
{'Ok_': {'result': 5}}
```

So codegen is very lightweight:

1. point at a Telepact server
2. generate bindings
3. use them with the Telepact runtime library

Use it when those generated bindings are genuinely helpful. Otherwise, it is
fine to stay with the runtime client and mock-driven validation workflow.

Next: [22. Minimum server](#22-minimum-server)

## 22. Minimum server

Now let's build our own Telepact server.

### Install the Python library

```sh
pip install --pre telepact
```

### Create a schema

Create `api/hello.telepact.yaml`:

```yaml
- info.Hello: {}

- fn.hello:
    name: string
  ->:
    - Ok_:
        message: string
```

### Create a tiny HTTP server

Create `server.py`:

```py
import asyncio
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from telepact import FunctionRouter, Message, Server, TelepactSchema


schema = TelepactSchema.from_directory('./api')

options = Server.Options()


async def hello(function_name: str, request_message: Message) -> Message:
    name = request_message.body[function_name]['name']
    return Message({}, {'Ok_': {'message': f'Hello, {name}!'}})


function_router = FunctionRouter()
function_router.register_unauthenticated_routes({'fn.hello': hello})
telepact_server = Server(schema, function_router, options)


class Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        if self.path != '/api/telepact':
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get('Content-Length', '0'))
        request_bytes = self.rfile.read(content_length)
        response = asyncio.run(telepact_server.process(request_bytes))

        content_type = 'application/octet-stream' if '@bin_' in response.headers else 'application/json'
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.end_headers()
        self.wfile.write(response.bytes)

    def log_message(self, format_string: str, *args: object) -> None:
        return


ThreadingHTTPServer(('127.0.0.1', 8002), Handler).serve_forever()
```

### Run it

```sh
python server.py
```

### Call it with `curl`

```sh
curl -s localhost:8002/api/telepact -d '[{}, {"fn.hello": {"name": "Telepact"}}]'
```

```json
[{}, {"Ok_": {"message": "Hello, Telepact!"}}]
```

Even this tiny server already gives clients the standard Telepact experience:
`fn.ping_`, `fn.api_`, validation, select, binary, codegen, and mocking.

Next: [23. Logging](#23-logging)

## 23. Logging

For server-side observability, the two main hooks are middleware and `on_error`.

### Install the Python library

```sh
pip install --pre telepact
```

### Add logging to the minimum server

Here is the interesting part of `server.py`:

```py
import asyncio
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from telepact import Message, Server, TelepactError, TelepactSchema


logging.basicConfig(level=logging.INFO)
log = logging.getLogger('hello-server')

schema = TelepactSchema.from_directory('./api')

options = Server.Options()


async def middleware(request_message: Message, function_router) -> Message:
    function_name = request_message.get_body_target()
    log.info('start %s', function_name)
    try:
        return await function_router.route(request_message)
    finally:
        log.info('finish %s', function_name)


options.middleware = middleware


def on_error(error: TelepactError) -> None:
    log.exception('telepact error case_id=%s', error.case_id, exc_info=error)


options.on_error = on_error


async def hello(function_name: str, request_message: Message) -> Message:
    if request_message.body[function_name]['name'] == 'boom':
        raise RuntimeError('unexpected bug')
    return Message({}, {'Ok_': {'message': 'hello'}})
```

### Run the server on port 8002

```sh
python server.py
```

### See normal logging

```sh
curl -s localhost:8002/api/telepact -d '[{}, {"fn.hello": {"name": "Telepact"}}]'
```

We should see middleware logs around the request.

### See error logging

```sh
curl -s localhost:8002/api/telepact -d '[{}, {"fn.hello": {"name": "boom"}}]'
```

Response:

```json
[{}, {"ErrorUnknown_": {"caseId": "5941539f-127c-4c4d-8194-1648f679be92"}}]
```

And the server logs should contain the actual stack trace with the same
`case_id=5941539f-127c-4c4d-8194-1648f679be92`. That is the main operational
pattern: keep the wire response generic, and use the case ID to match a
client-side `ErrorUnknown_` report to the corresponding server-side log entry.

Next: [24. Server auth](#24-server-auth)

## 24. Server auth

Now let's add one piece of Telepact's auth convention to our own server.
For the full canonical path, see the
[Auth Guide](concepts.md#auth-guide).

### Install the Python library

```sh
pip install --pre telepact
```

### Add `union.Auth_` to the schema

```yaml
- union.Auth_:
    - Password:
        password: string

- fn.secret: {}
  ->:
    - Ok_:
        message: string
```

### Implement `on_auth`

```py
from telepact import Message, Server

options = Server.Options()


def on_auth(headers: dict[str, object]) -> dict[str, object]:
    auth = headers.get('@auth_')
    if auth == {'Password': {'password': 'swordfish'}}:
        return {'@role': 'admin'}
    raise ValueError('missing or invalid credentials')


options.on_auth = on_auth


async def secret(function_name: str, request_message: Message) -> Message:
    return Message({}, {'Ok_': {'message': 'welcome'}})
```

The important shape here is:

1. read credentials from `@auth_`
2. validate them in `on_auth`
3. return normalized identity or authorization headers for later handlers
4. register protected handlers in the authenticated route map so missing
    credentials automatically become `ErrorUnauthenticated_`

That normalization step is the core Telepact server-side auth pattern.
If validation fails, throw in `on_auth` rather than returning an empty identity
and checking for it later in shared middleware.

### Call it

Without auth:

```sh
curl -s localhost:8002/api/telepact -d '[{}, {"fn.secret": {}}]'
```

With auth:

```sh
curl -s localhost:8002/api/telepact -d '[{"@auth_": {"Password": {"password": "swordfish"}}}, {"fn.secret": {}}]'
```

This keeps the public credential shape in the schema and the auth normalization
logic in one clear place.

Next: [25. Managed auth](#25-managed-auth)

## 25. Managed auth

Sometimes the client is not going to handcraft `@auth_` at all. Cookies are the
common example.

This page shows one browser/session-cookie branch of Telepact's auth
convention. For the full canonical path, see the
[Auth Guide](concepts.md#auth-guide).

### Install the Python library

```sh
pip install --pre telepact
```

### Use a session-shaped `union.Auth_`

```yaml
- union.Auth_:
    - Session:
        token: string
```

### Inject `@auth_` from the transport layer

Here is the key pattern:

```py
import asyncio
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler


def read_session_cookie(cookie_header: str | None) -> str | None:
    if not cookie_header:
        return None

    cookie = SimpleCookie()
    cookie.load(cookie_header)
    session = cookie.get('session')
    return session.value if session is not None else None


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        content_length = int(self.headers.get('Content-Length', '0'))
        request_bytes = self.rfile.read(content_length)
        session_token = read_session_cookie(self.headers.get('Cookie'))

        def update_headers(headers: dict[str, object]) -> None:
            if session_token is not None:
                headers['@auth_'] = {'Session': {'token': session_token}}

        response = asyncio.run(telepact_server.process(request_bytes, update_headers))
```

Now the rest of our auth story can stay the same:

- `union.Auth_` still defines the credential shape
- `on_auth` still validates it
- handlers still work with normalized identity headers

From the client's perspective, auth can be "managed" by the transport. That is a
nice fit for browser cookies, while still converging on the canonical `@auth_`
shape inside the Telepact server.

Next: [26. Schema evolution](#26-schema-evolution)

## 26. Schema evolution

Telepact encourages us to evolve schemas carefully and keep them backwards
compatible.

### Install the CLI

```sh
uv tool install --prerelease=allow telepact-cli
```

### Create an old schema

`old/api.telepact.yaml`:

```yaml
- fn.hello:
    name: string
  ->:
    - Ok_:
        message: string
```

### Create a compatible new schema

`new-ok/api.telepact.yaml`:

```yaml
- fn.hello:
    name: string
    punctuation!: string
  ->:
    - Ok_:
        message: string
```

Compare them:

```sh
telepact compare --old-schema-dir ./old --new-schema-dir ./new-ok
```

Output:

```text
Schemas are backwards compatible.
```

That succeeds, because we only added an optional argument field.

### Create an incompatible new schema

`new-bad/api.telepact.yaml`:

```yaml
- fn.hello:
    name: integer
  ->:
    - Ok_:
        message: string
```

Compare again:

```sh
telepact compare --old-schema-dir ./old --new-schema-dir ./new-bad
```

Output:

```text
Backwards incompatible change(s) found:
 - Field 'name' in struct 'fn.hello' has changed type from 'string' to 'integer'
```

This is the workflow we want in server development: evolve the schema, then let
`telepact compare` keep us honest.

For the practical Git-based workflow to compare the checked-in schema directory
on your branch with `origin/main` or a release tag, see
[Tooling Workflow: Compare schema versions](../../../build-clients-and-servers/tooling-workflow.md#compare-schema-versions).

Next: [27. TDD with TestClient](#27-tdd-with-testclient)

## 27. TDD with TestClient

Let's test our own Telepact server directly, without even starting HTTP.

### Install what this example needs

```sh
pip install --pre telepact pytest
```

### Reuse the minimum server, but leave one bug in it

Create `server.py`:

```py
from telepact import FunctionRouter, Message, Server, TelepactSchema


schema = TelepactSchema.from_directory('./api')

options = Server.Options()


async def hello(function_name: str, request_message: Message) -> Message:
    name = request_message.body[function_name]['name']
    return Message({}, {'Ok_': {'message': name}})


function_router = FunctionRouter()
function_router.register_unauthenticated_routes({'fn.hello': hello})
telepact_server = Server(schema, function_router, options)
```

That is intentionally wrong. We want `Hello, Telepact!`, but the server only
returns `Telepact`.

### Point a client at `telepact_server.process(...)`

Create `test_server.py`:

```py
import asyncio

import pytest

from telepact import Client, Message, Serializer, TestClient
from server import telepact_server


async def adapter(message: Message, serializer: Serializer) -> Message:
    request_bytes = serializer.serialize(message)
    response = await telepact_server.process(request_bytes)
    return serializer.deserialize(response.bytes)


def make_test_client() -> TestClient:
    client = Client(adapter, Client.Options())
    return TestClient(client, TestClient.Options())


def test_hello_shows_the_actual_payload() -> None:
    test_client = make_test_client()

    with pytest.raises(AssertionError) as error_info:
        asyncio.run(
            test_client.assert_request(
                Message({}, {'fn.hello': {'name': 'Telepact'}}),
                {'Ok_': {'message': 'Hello, Telepact!'}},
                True,
            )
        )

    assert "Actual: {'Ok_': {'message': 'Telepact'}}" in str(error_info.value)


def test_hello_can_keep_going_with_multiple_assertions() -> None:
    test_client = make_test_client()

    response = asyncio.run(
        test_client.assert_request(
            Message({}, {'fn.hello': {'name': 'Telepact'}}),
            {'Ok_': {'message': 'Hello, Telepact!'}},
            False,
        )
    )

    greeting = response.body['Ok_']['message']

    assert greeting.startswith('Hello, ')
    extracted_name = greeting.removeprefix('Hello, ')
    assert extracted_name == 'Telepact!'
```

### Run the tests

```sh
pytest -q
```

The first test is the usual red phase: the assertion fails, and the error text
includes the actual payload that came back from the server.

The second test shows the more unusual part. It uses `expect_match=False`,
which means we currently expect the server to *not* match yet. In that case,
`TestClient` returns a schema-valid response built from the expected payload we
supplied, so the test can keep going.

That matters when one assertion depends on the result of an earlier one. Here,
the server really returned `Telepact`, but `TestClient` hands the test a
response whose `message` still satisfies the expected shape. That lets us first
assert `startswith('Hello, ')` and then use that result for the next assertion
on `Telepact!`, all in one red-phase test.

### Fix the server

Once we are ready to make the test green, change the handler:

```py
async def hello(function_name: str, request_message: Message) -> Message:
    name = request_message.body[function_name]['name']
    return Message({}, {'Ok_': {'message': f'Hello, {name}!'}})
```

Now we can switch back to `expect_match=True` and keep the strict assertion.

Next: [28. Best practices for server implementers](#28-best-practices-for-server-implementers)

## 28. Best practices for server implementers

Let's finish by pulling the server-side lessons together.

### 1. Be explicit in the schema

If clients are expected to use a field, type, function, or header directly,
define it clearly in the schema and document it with `///`.

### 2. Use the best data shape, not a vague error

Prefer expressive data over HTTP-shaped habits:

- prefer optional fields over "404 not found"
- let Telepact handle request validation instead of inventing a generic "400"
- use function-specific errors for real business rules

The [FAQ](concepts.md#faq) is worth reading end to end here.

### 3. Log on the server

Keep request lifecycle logging in middleware and error details in `on_error`.
Clients may only see `ErrorUnknown_`, so logs are where operational detail lives.

### 4. Favor backwards compatibility

Treat schema evolution as a normal part of development and check it with
`telepact compare`.

### 5. Let Telepact do the ecosystem work

Once the server uses a Telepact library correctly, clients can choose the level
of tooling they want:

- raw `curl`
- runtime clients
- field selection
- binary
- mocks
- code generation

That breadth is one of Telepact's best qualities: clients can start simple and
grow into richer tooling without the server changing its basic contract style.

Next: [Back to the start](#00-installation)
