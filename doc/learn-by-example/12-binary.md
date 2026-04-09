# 12. Opt-in features: Binary

Let's switch from “JSON everywhere” to “binary when we want it.”

## Start the demo server

```sh
cd sdk/cli
uv run telepact demo-server --port 8000
```

## Create a slightly larger response

`fn.getPaperTape` is more interesting after we record a couple of evaluations:

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 2}}, "right": {"Constant": {"value": 3}}}}}}]'
curl http://localhost:8000/api -X POST --data '[{}, {"fn.evaluate": {"expression": {"Mul": {"left": {"Constant": {"value": 4}}, "right": {"Constant": {"value": 5}}}}}}]'
```

A normal JSON response looks like this:

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.getPaperTape": {"limit!": 2}}]'
```

```jsonc
[{}, {"Ok_": {"tape": [{"expression": {"Mul": ...}, "result": 20, ...}, {"expression": {"Add": ...}, "result": 5, ...}]}}]
```

In one run, that response was 342 bytes.

## Ask for binary without a negotiated policy

```sh
curl http://localhost:8000/api -X POST --data '[{"@bin_": []}, {"fn.getPaperTape": {"limit!": 2}}]' | xxd -g 1 -l 48
```

```text
00000000: 92 82 a5 40 65 6e 63 5f de 00 29 a3 41 64 64 00  ...@enc_..).Add.
00000010: a8 43 6f 6e 73 74 61 6e 74 01 a3 44 69 76 02 a3  .Constant..Div..
00000020: 4d 75 6c 03 a3 4f 6b 5f 04 a3 53 75 62 05 a8 56  Mul..Ok_..Sub..V
```

That looks like binary data because it is binary data. On one run, this first binary response was 500 bytes because the server also had to send:

- an `@enc_` field map
- an `@bin_` checksum id

On that run the checksum was `532741750`, so let's send it back.

## Reuse the negotiated checksum

```sh
curl http://localhost:8000/api -X POST --data '[{"@bin_": [532741750]}, {"fn.getPaperTape": {"limit!": 2}}]' | xxd -g 1 -l 48
```

```text
00000000: 92 81 a5 40 62 69 6e 5f 91 ce 1f c0 fe 76 81 04  ...@bin_.....v..
00000010: 81 20 92 84 08 81 03 82 18 81 01 81 24 04 1d 81  . .........$...
00000020: 01 81 24 05 1c 14 21 ce 69 d7 c2 8d 1f c3 84 08  ..$...!.i.......
```

Now the same response was only 73 bytes.

That runtime negotiation is a big Telepact differentiator. Unlike codegen-first binary systems such as gRPC, Telepact can negotiate binary at runtime, so clients do not need generated code just to speak a compact wire format.

In normal client code, we should not hardcode `@bin_` manually. A Telepact runtime client can set `useBinary: true`, and the negotiation plus checksum caching happens for us. That cache is a great fit here because the encoding only changes when the server schema changes.

Telepact's binary protocol is powered by [MessagePack](https://msgpack.org/).

Next: [13. Mock server](./13-mock-server.md)
