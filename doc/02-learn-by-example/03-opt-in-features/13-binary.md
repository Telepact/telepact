# 13. Binary

Telepact can also switch the whole message envelope into a compact binary form.

## Start the demo server

```sh
telepact demo-server --port 8000
```

## Seed a little data

```sh
curl -s localhost:8000/api -d '[{}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 2}}, "right": {"Constant": {"value": 3}}}}}}]'
curl -s localhost:8000/api -d '[{}, {"fn.evaluate": {"expression": {"Variable": {"name": "x"}}}}]'
```

## Measure plain JSON first

```sh
curl -s localhost:8000/api -d '[{}, {"fn.getPaperTape": {}}]' | wc -c
```

On one run, that was:

```text
444
```

## Do the binary handshake

First request:

```sh
curl -s localhost:8000/api -d '[{"@bin_": []}, {"fn.getPaperTape": {}}]' > /tmp/papertape-first.bin
wc -c < /tmp/papertape-first.bin
xxd -g 1 -l 64 /tmp/papertape-first.bin
```

On one run, that first binary response was larger:

```text
546
```

That is expected. We told the server we had no negotiated binary policy yet, so
it returned binary data *plus* the field map in `@enc_`.

Now let's extract the negotiated checksum:

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

And use it on the next request:

```sh
curl -s localhost:8000/api -d "[{\"@bin_\": [$checksum]}, {\"fn.getPaperTape\": {}}]" > /tmp/papertape-steady.bin
wc -c < /tmp/papertape-steady.bin
xxd -g 1 -l 64 /tmp/papertape-steady.bin
```

On one run, the steady-state binary response dropped to:

```text
91
```

That is the differentiator: Telepact negotiates binary **at runtime** instead of
forcing us into a codegen-managed ABI workflow.

Under the hood, this binary format is powered by [MessagePack](https://msgpack.org/).

In normal client code, we should not handcraft `@bin_` like this. A Telepact
runtime client can do the negotiation and caching for us automatically.

Next: [14. Mock server](../../04-mocking-an-integration/14-mock-server.md)
