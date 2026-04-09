# 12. Binary

Let's look at Telepact's binary mode, which is negotiated at runtime rather
than generated ahead of time.

## Start a fresh demo server

```sh
telepact demo-server --port 8011
```

Let's record two evaluations so the tape response has some shape to work with:

```sh
curl -s http://127.0.0.1:8011/api -X POST -d '[{}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 7}}, "right": {"Constant": {"value": 8}}}}}}]'
curl -s http://127.0.0.1:8011/api -X POST -d '[{}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 7}}, "right": {"Constant": {"value": 8}}}}}}]'
```

A normal JSON response looks like this:

```sh
curl -s http://127.0.0.1:8011/api -X POST -d '[{}, {"fn.getPaperTape": {"limit!": 2}}]'
```

```json
[{}, {"Ok_": {"tape": [{"expression": {"Add": {"left": {"Constant": {"value": 7}}, "right": {"Constant": {"value": 8}}}}, "result": 15, "timestamp": ..., "successful": true}, {"expression": {"Add": {"left": {"Constant": {"value": 7}}, "right": {"Constant": {"value": 8}}}}, "result": 15, "timestamp": ..., "successful": true}]}}]
```

Now let's opt into binary with an empty policy list, which means "we have not
negotiated anything yet":

```sh
curl -s http://127.0.0.1:8011/api -X POST -d '[{"@bin_": []}, {"fn.getPaperTape": {"limit!": 2}}]' > first.bin
wc -c first.bin
```

```text
500 first.bin
```

If `xxd` is available, we can peek at the bytes and see that the response is no
longer plain JSON:

```sh
xxd -l 64 -g 1 first.bin
```

```text
00000000: 92 82 a5 40 65 6e 63 5f de 00 29 a3 41 64 64 00  ...@enc_..).Add.
00000010: a8 43 6f 6e 73 74 61 6e 74 01 a3 44 69 76 02 a3  .Constant..Div..
00000020: 4d 75 6c 03 a3 4f 6b 5f 04 a3 53 75 62 05 a8 56  Mul..Ok_..Sub..V
00000030: 61 72 69 61 62 6c 65 06 a3 61 70 69 07 aa 65 78  ariable..api..ex
```

That first binary response is actually a little bigger because the server had to
send us two things at once:

- a binary encoding map in `@enc_`
- a binary protocol id in `@bin_`

In this run, the id was `532741750`, so now we can send it back:

```sh
curl -s http://127.0.0.1:8011/api -X POST -d '[{"@bin_": [532741750]}, {"fn.getPaperTape": {"limit!": 2}}]' > second.bin
wc -c second.bin
```

```text
73 second.bin
```

That byte drop is the whole point of the handshake. Once client and server agree
on the field map, the payload gets much smaller.

This is a big Telepact differentiator: binary without generated code. In normal
client code, we would not hardcode `@bin_` ourselves. We would use a Telepact
runtime client, set `useBinary` to `true`, and let it negotiate and cache the
binary protocol for us. That cache works especially well because schema changes
are infrequent.

Under the hood, this binary mode is powered by [MessagePack](https://msgpack.org/).

Next: [13. Mock server](./13-mock-server.md)
