# 12. Binary

Let's try Telepact's other big opt-in feature: binary payloads.

If we don't already have the published CLI, let's install it:

```sh
uv tool install --prerelease=allow telepact-cli
```

In one terminal, let's start the demo server:

```sh
telepact demo-server --port 8000
```

In a second terminal, let's seed a richer response payload. The paper tape is
filled by evaluations, so let's record two of them:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 1}}, "right": {"Constant": {"value": 2}}}}}}]'

curl -s http://localhost:8000/api \
  --data '[{}, {"fn.evaluate": {"expression": {"Mul": {"left": {"Constant": {"value": 3}}, "right": {"Constant": {"value": 4}}}}}}]'

curl -s http://localhost:8000/api \
  --data '[{}, {"fn.getPaperTape": {}}]'
```

That last response is ordinary JSON.

Now let's opt into binary negotiation:

```sh
curl -s http://localhost:8000/api \
  --data '[{"@bin_": []}, {"fn.getPaperTape": {}}]' | xxd -l 96 -g 1
```

Example output:

```text
00000000: 92 82 a5 40 65 6e 63 5f de 00 29 a3 41 64 64 00  ...@enc_..).Add.
00000010: a8 43 6f 6e 73 74 61 6e 74 01 a3 44 69 76 02 a3  .Constant..Div..
00000020: 4d 75 6c 03 a3 4f 6b 5f 04 a3 53 75 62 05 a8 56  Mul..Ok_..Sub..V
...
```

That looks bigger and noisier because we told the server we had no binary policy
cached yet. So the server included the field map and a binary id for that map.
In one run, that checksum was `532741750`.

Using that negotiated id, the next response gets much smaller byte-for-byte:

```sh
curl -s http://localhost:8000/api \
  --data '[{"@bin_": [532741750]}, {"fn.getPaperTape": {}}]' | xxd -l 96 -g 1

curl -s http://localhost:8000/api \
  --data '[{"@bin_": []}, {"fn.getPaperTape": {}}]' | wc -c

curl -s http://localhost:8000/api \
  --data '[{"@bin_": [532741750]}, {"fn.getPaperTape": {}}]' | wc -c
```

Example sizes from this run:

```text
654
227
```

That runtime negotiation is one of Telepact's big differentiators. Unlike gRPC-
style code generation pipelines, Telepact can negotiate binary at runtime, so
clients do not need generated code just to use binary. It is a natural fit for
caching too, because the negotiation only needs to happen again when the API
schema changes.

Under the hood, this binary protocol is powered by [MessagePack](https://msgpack.org/).

In real client code, we usually would not hand-write `@bin_` like this. We
would use a Telepact runtime client, set `useBinary` to `true`, and let the
client handle negotiation and caching for us.

Next: [13. Mock server](./13-mocking-mock-server.md)
