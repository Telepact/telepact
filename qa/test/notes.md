potential new format:

```json
{
  "_ping": {},
  ".ctx": {
    "Authorization": "Bearer <token>"
  }
}
```

```json

[[]]
[]

42:0
[[42]],
["ida-1"]

42:0, 10:1
[[42, 10]],
["ida-1", true]

42:0, 10:1, 8:2
[
  [42, 10, 8],
  []
],
["ida-1", true, []]

42:0,0 10:0,1 8:0,2 65:1,0
[null, 42, 10, [8, 12]]
["ida-1", true, ["idb-1"]]


[1, 2, [3, 4, 5], 6],
["id-1", false, ["id-2", 0], "world"]

[1, 2, [3, 4, 5], 6],
["id-1", false, ["id-2", 0], "world"]
```
