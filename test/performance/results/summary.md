# Telepact performance summary

This checked-in snapshot mirrors the benchmark summary referenced by
[`doc/operate/binary-performance-guide.md`](../../../doc/operate/binary-performance-guide.md).

## Overall median across all languages, data shapes, and collection shapes

| Network | Method | Median request size (bytes) | Median total latency (ms) |
| --- | --- | ---: | ---: |
| close | Telepact JSON | 6362.0 | 0.6818 |
| close | Telepact binary | 2538.0 | 0.8520 |
| close | Telepact packed binary | 2235.0 | 0.7551 |
| close | protobuf | 2379.0 | 0.4265 |
| close | plain JSON | 6350.0 | 0.5211 |
| far | Telepact JSON | 6362.0 | 64.9141 |
| far | Telepact binary | 2538.0 | 65.0361 |
| far | Telepact packed binary | 2235.0 | 65.0139 |
| far | protobuf | 2379.0 | 64.5925 |
| far | plain JSON | 6350.0 | 64.8628 |

## Representative size results

### Typical data, really big list, close network (median across Python, TypeScript, Java)

| Method | Request bytes | Response bytes | Total latency (ms) |
| --- | ---: | ---: | ---: |
| Telepact JSON | 50532 | 50503 | 1.1745 |
| Telepact binary | 20082 | 20072 | 1.9401 |
| Telepact packed binary | 17539 | 17529 | 1.7208 |
| protobuf | 19027 | 19027 | 0.5978 |
| plain JSON | 50520 | 50520 | 1.5092 |

### All-numbers data, really big list, close network (median across Python, TypeScript, Java)

| Method | Request bytes | Response bytes | Total latency (ms) |
| --- | ---: | ---: | ---: |
| Telepact JSON | 42933 | 42904 | 1.4395 |
| Telepact binary | 20739 | 20729 | 1.5164 |
| Telepact packed binary | 18196 | 18186 | 1.4330 |
| protobuf | 18354 | 18354 | 0.4476 |
| plain JSON | 42921 | 42921 | 1.3567 |

### Typical data, single item, close network (median across Python, TypeScript, Java)

| Method | Request bytes | Response bytes | Total latency (ms) |
| --- | ---: | ---: | ---: |
| Telepact JSON | 150 | 121 | 0.5009 |
| Telepact binary | 67 | 57 | 0.4609 |
| Telepact packed binary | 79 | 69 | 0.5812 |
| protobuf | 36 | 36 | 0.3845 |
| plain JSON | 138 | 138 | 0.3406 |

### All-numbers data, huge list, far network (median across Python, TypeScript, Java)

| Method | Request bytes | Response bytes | Total latency (ms) |
| --- | ---: | ---: | ---: |
| Telepact JSON | 101035 | 101006 | 68.4777 |
| Telepact binary | 48669 | 48659 | 68.1286 |
| Telepact packed binary | 42686 | 42676 | 68.0228 |
| protobuf | 43044 | 43044 | 65.2120 |
| plain JSON | 101023 | 101023 | 68.8954 |
