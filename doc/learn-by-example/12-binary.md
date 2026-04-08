# 12. Binary

Telepact can also negotiate binary request and response payloads at runtime.
That is one of its unusual strengths.

Let's prepare some paper-tape data first:

```sh
curl -s localhost:8000/api -d '[{"@auth_": {"Ephemeral": {"username": "binary-guide"}}}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 1}}, "right": {"Constant": {"value": 2}}}}}}]' > /dev/null
curl -s localhost:8000/api -d '[{"@auth_": {"Ephemeral": {"username": "binary-guide"}}}, {"fn.evaluate": {"expression": {"Mul": {"left": {"Constant": {"value": 3}}, "right": {"Constant": {"value": 4}}}}}}]' > /dev/null
```

Here is the normal JSON response from `fn.getPaperTape`:

```sh
curl -s localhost:8000/api -d '[{"@auth_": {"Ephemeral": {"username": "binary-guide"}}}, {"fn.getPaperTape": {"limit!": 2}}]' | python -m json.tool
```

```json
[
  {},
  {
    "Ok_": {
      "tape": [
        {
          "expression": {"Mul": {"left": {"Constant": {"value": 3}}, "right": {"Constant": {"value": 4}}}},
          "result": 12,
          "timestamp": 1775686392,
          "successful": true
        },
        {
          "expression": {"Add": {"left": {"Constant": {"value": 1}}, "right": {"Constant": {"value": 2}}}},
          "result": 3,
          "timestamp": 1775686392,
          "successful": true
        }
      ]
    }
  }
]
```

Now let's opt in to binary by sending `@bin_` with an empty array. That means
"we want binary, but we do not have a negotiated field map yet."

```sh
curl -s localhost:8000/api -d '[{"@auth_": {"Ephemeral": {"username": "binary-guide"}}, "@bin_": []}, {"fn.getPaperTape": {"limit!": 2}}]' | xxd -g 1 | head -n 4
```

```text
00000000: 92 82 a5 40 65 6e 63 5f de 00 29 a3 41 64 64 00  ...@enc_..).Add.
00000010: a8 43 6f 6e 73 74 61 6e 74 01 a3 44 69 76 02 a3  .Constant..Div..
00000020: 4d 75 6c 03 a3 4f 6b 5f 04 a3 53 75 62 05 a8 56  Mul..Ok_..Sub..V
00000030: 61 72 69 61 62 6c 65 06 a3 61 70 69 07 aa 65 78  ariable..api..ex
```

That first binary response is actually larger, because the server had to send
both the negotiated checksum and the `@enc_` field map. In this run, the
checksum was `532741750`.

We can see the size tradeoff directly:

```sh
printf 'json '; curl -s localhost:8000/api -d '[{"@auth_": {"Ephemeral": {"username": "binary-guide"}}}, {"fn.getPaperTape": {"limit!": 2}}]' | wc -c
printf 'bin handshake '; curl -s localhost:8000/api -d '[{"@auth_": {"Ephemeral": {"username": "binary-guide"}}, "@bin_": []}, {"fn.getPaperTape": {"limit!": 2}}]' | wc -c
printf 'bin cached '; curl -s localhost:8000/api -d '[{"@auth_": {"Ephemeral": {"username": "binary-guide"}}, "@bin_": [532741750]}, {"fn.getPaperTape": {"limit!": 2}}]' | wc -c
```

```text
json 342
bin handshake 500
bin cached 73
```

After that handshake, the cached binary response is much smaller:

```sh
curl -s localhost:8000/api -d '[{"@auth_": {"Ephemeral": {"username": "binary-guide"}}, "@bin_": [532741750]}, {"fn.getPaperTape": {"limit!": 2}}]' | xxd -g 1 | head -n 4
```

```text
00000000: 92 81 a5 40 62 69 6e 5f 91 ce 1f c0 fe 76 81 04  ...@bin_.....v..
00000010: 81 20 92 84 08 81 03 82 18 81 01 81 24 03 1d 81  . ..........$...
00000020: 01 81 24 04 1c 0c 21 ce 69 d6 d2 f8 1f c3 84 08  ..$...!.i.......
00000030: 81 00 82 18 81 01 81 24 01 1d 81 01 81 24 02 1c  .......$.....$..
```

This is the differentiator: Telepact does binary through runtime negotiation,
not through a code-generation distribution pipeline. In normal client code we
would not hardcode `@bin_` ourselves. We'd use a Telepact runtime client and set
`useBinary: true`, and the client would cache the negotiated protocol for us.

That cache is a great fit here because the binary map only needs to change when
the API schema changes, which is usually infrequent. Under the hood, this binary
protocol is powered by [MessagePack](https://msgpack.org/).

Next, let's switch from a live server to a mock integration in
[13-mock-server.md](./13-mock-server.md).
