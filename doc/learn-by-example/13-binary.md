# 13. Binary

Telepact can switch the whole message envelope into a compact binary form.
The nice part is that it is **opt-in at runtime**: the client asks for binary,
the server negotiates a field map once, and the steady-state payload gets much
smaller.

## Start the demo server

```sh
telepact demo-server --port 8000
```

## Seed a little data

```sh
curl -s localhost:8000/api -d '[{}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 2}}, "right": {"Constant": {"value": 3}}}}}}]'
curl -s localhost:8000/api -d '[{}, {"fn.evaluate": {"expression": {"Variable": {"name": "x"}}}}]'
```

## The function we are calling

```yaml
- fn.getPaperTape:
    limit!: integer
  ->:
    - Ok_:
        tape: [struct.Evaluation]
```

## Visualize the negotiation

| Step | Request header | What comes back | Size from one run |
| --- | --- | --- | --- |
| Plain JSON | none | readable JSON | 289 B |
| First binary response | `"@bin_": []` | binary body + `@enc_` map | 527 B |
| Negotiated binary response | `"@bin_": [900069279]` | compact binary body only | 72 B |

The first binary response is bigger because the server has to teach us the
encoding map. After that, the checksum in `@bin_` is enough.

## 1. Plain JSON baseline

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

## 2. Ask for binary

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

## 3. Reuse the negotiated checksum

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

Next: [14. Mock server](./14-mock-server.md)
