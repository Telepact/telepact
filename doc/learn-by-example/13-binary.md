# 13. Binary

Telepact can switch the same message envelope into a compact binary form. The
key idea is that binary is **opt-in** and negotiated **at runtime**.

## Start the demo server

```sh
telepact demo-server --port 8000
```

## Seed a little data

```sh
curl -s localhost:8000/api -d '[{}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 2}}, "right": {"Constant": {"value": 3}}}}}}]'
curl -s localhost:8000/api -d '[{}, {"fn.evaluate": {"expression": {"Variable": {"name": "x"}}}}]'
```

## The call we are measuring

```yaml
- fn.getPaperTape:
    limit!: integer
  ->:
    - Ok_:
        tape: [struct.Evaluation]
```

We will make the same `fn.getPaperTape` call three times and compare what goes
over the wire. The `!` means `limit` is optional, as in the earlier examples.
Exact timestamps and the negotiated checksum will vary between runs.

## 1. Plain JSON

```sh
curl -s localhost:8000/api -d '[{}, {"fn.getPaperTape": {}}]' > /tmp/papertape.json
wc -c < /tmp/papertape.json
```

On one run:

```text
289
```

Visualization:

```text
Request
[{}, {"fn.getPaperTape": {}}]

Response · 289 B
[{}, {"Ok_": {"tape": [{"expression": {"Variable": {"name": "x"}}, "result": 0.0, "timestamp": 1776266103, "successful": false}, {"expression": {"Add": {"left": {"Constant": {"value": 2}}, "right": {"Constant": {"value": 3}}}}, "result": 5, "timestamp": 1776266103, "successful": true}]}}]
```

## 2. First binary response: negotiate field ids

```sh
curl -s localhost:8000/api -d '[{"@bin_": []}, {"fn.getPaperTape": {}}]' > /tmp/papertape-first.bin
wc -c < /tmp/papertape-first.bin
```

On one run, the first binary response was larger:

```text
527
```

Visualization:

```text
Request
[{"@bin_": []}, {"fn.getPaperTape": {}}]

Response · 527 B
headers: {
  "@bin_": [900069279],
  "@enc_": { ... negotiated field ids ... }
}

payload (ASCII view):
...@enc_..,.Add..Constant..Div..Mul..Ok_..Sub..Variable..api..
blob..expression..fn.add..fn.api_.
```

That first response is larger because the server has to send the negotiated
field map in `@enc_` along with the binary checksum in `@bin_`.

## 3. Steady-state binary: reuse the checksum

Extract the negotiated checksum:

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

Now send it back:

```sh
curl -s localhost:8000/api -d "[{\"@bin_\": [$checksum]}, {\"fn.getPaperTape\": {}}]" > /tmp/papertape-steady.bin
wc -c < /tmp/papertape-steady.bin
```

On one run, the steady-state binary response dropped to:

```text
72
```

Visualization:

```text
Request
[{"@bin_": [900069279]}, {"fn.getPaperTape": {}}]

Response · 72 B
headers: {
  "@bin_": [900069279]
}

payload (ASCII view):
...@bin_..5......#........x.........$.i..w"..........'.
...'...$.i..w".
```

## What changed on the wire?

| Wire format | What the server includes | Example size |
| --- | --- | --- |
| Plain JSON | JSON body only | 289 B |
| First binary response | binary body + `@bin_` + `@enc_` | 527 B |
| Negotiated binary response | binary body + `@bin_` | 72 B |

```text
Plain JSON                  289 B  ███████████████
First binary response       527 B  ███████████████████████████
Negotiated binary response   72 B  ████
```

So the protocol works like this:

1. the client opts into binary with `@bin_`: `[]`
2. the server replies with binary bytes plus the field-id map in `@enc_`
3. the client caches the checksum from `@bin_` and reuses it
4. later messages stay compact because `@enc_` no longer needs to be resent

Under the hood, this binary format is powered by [MessagePack](https://msgpack.org/).

In normal client code, we should not handcraft `@bin_` like this. A Telepact
runtime client can do the negotiation and caching for us automatically, which is
what we will do next.

Next: [14. Mock server](./14-mock-server.md)
