# Performance Rollup

- raw samples: `smoke-all.jsonl`
- summaries: `smoke-all.csv`

## close

| language | method | median request size (bytes) | median response size (bytes) | median request transit (ms) | median response transit (ms) |
| --- | --- | ---: | ---: | ---: | ---: |
| python | telepact-json | 169.0 | 151.0 | 0.203093 | 0.187495 |
| python | telepact-binary | 80.0 | 70.0 | 0.188807 | 0.239056 |
| python | protobuf | 50.0 | 50.0 | 0.185481 | 0.178047 |
| python | plain-json | 137.0 | 137.0 | 0.188511 | 0.195705 |
| typescript | telepact-json | 153.0 | 136.0 | 0.324114 | 0.283914 |
| typescript | telepact-binary | 82.0 | 72.0 | 0.325607 | 0.313238 |
| typescript | protobuf | 50.0 | 50.0 | 0.335997 | 0.34258 |
| typescript | plain-json | 137.0 | 137.0 | 0.295612 | 0.402631 |
| java | telepact-json | 153.0 | 136.0 | 0.280752 | 0.313221 |
| java | telepact-binary | 80.0 | 70.0 | 0.306267 | 0.343197 |
| java | protobuf | 50.0 | 50.0 | 0.329935 | 0.308332 |
| java | plain-json | 137.0 | 137.0 | 0.322177 | 0.286017 |

