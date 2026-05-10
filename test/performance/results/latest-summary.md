# Performance Harness Summary

- NATS URL: `nats://127.0.0.1:4222`
- Warmup iterations per case: 2
- Measured iterations per case: 5

All Telepact binary measurements exclude warmup samples so binary encoding negotiation traffic is not counted.

## Python

| Method | Data shape | Collection shape | Req bytes mean | Resp bytes mean | Req transit p95 (ms) | Resp transit p95 (ms) | Client req serialize mean (ms) | Client resp deserialize mean (ms) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `telepact_json` | `typical_data` | `single` | 160.00 | 133.00 | 0.141 | 0.178 | 0.012 | 0.015 |
| `telepact_json` | `typical_data` | `small_list` | 1172.00 | 1147.00 | 0.142 | 0.183 | 0.031 | 0.022 |
| `telepact_json` | `typical_data` | `big_list` | 11344.00 | 11319.00 | 0.165 | 0.218 | 0.181 | 0.096 |
| `telepact_json` | `typical_data` | `really_big_list` | 113055.00 | 113030.00 | 0.609 | 0.695 | 1.692 | 0.777 |
| `telepact_json` | `all_strings` | `single` | 209.00 | 182.00 | 0.161 | 0.170 | 0.010 | 0.012 |
| `telepact_json` | `all_strings` | `small_list` | 1641.00 | 1616.00 | 0.151 | 0.175 | 0.024 | 0.017 |
| `telepact_json` | `all_strings` | `big_list` | 15951.00 | 15926.00 | 0.183 | 0.211 | 0.148 | 0.061 |
| `telepact_json` | `all_strings` | `really_big_list` | 159051.00 | 159026.00 | 0.499 | 0.854 | 1.301 | 0.473 |
| `telepact_json` | `all_numbers` | `single` | 123.00 | 96.00 | 0.141 | 0.174 | 0.011 | 0.013 |
| `telepact_json` | `all_numbers` | `small_list` | 866.00 | 841.00 | 0.156 | 0.153 | 0.029 | 0.021 |
| `telepact_json` | `all_numbers` | `big_list` | 8642.00 | 8617.00 | 0.176 | 0.205 | 0.183 | 0.090 |
| `telepact_json` | `all_numbers` | `really_big_list` | 91677.00 | 91652.00 | 0.407 | 0.534 | 1.698 | 0.818 |
| `telepact_binary` | `typical_data` | `single` | 79.00 | 69.00 | 0.157 | 0.174 | 0.013 | 0.022 |
| `telepact_binary` | `typical_data` | `small_list` | 547.00 | 537.00 | 0.160 | 0.174 | 0.026 | 0.066 |
| `telepact_binary` | `typical_data` | `big_list` | 5371.00 | 5361.00 | 0.178 | 0.217 | 0.160 | 0.479 |
| `telepact_binary` | `typical_data` | `really_big_list` | 53641.00 | 53631.00 | 0.347 | 0.531 | 1.456 | 6.005 |
| `telepact_binary` | `all_strings` | `single` | 130.00 | 120.00 | 0.180 | 0.205 | 0.012 | 0.022 |
| `telepact_binary` | `all_strings` | `small_list` | 1049.00 | 1039.00 | 0.149 | 0.170 | 0.023 | 0.055 |
| `telepact_binary` | `all_strings` | `big_list` | 10231.00 | 10221.00 | 0.159 | 0.210 | 0.128 | 0.402 |
| `telepact_binary` | `all_strings` | `really_big_list` | 102031.00 | 102021.00 | 0.381 | 0.594 | 1.198 | 3.936 |
| `telepact_binary` | `all_numbers` | `single` | 55.00 | 45.00 | 0.178 | 0.176 | 0.012 | 0.021 |
| `telepact_binary` | `all_numbers` | `small_list` | 299.00 | 289.00 | 0.157 | 0.160 | 0.027 | 0.055 |
| `telepact_binary` | `all_numbers` | `big_list` | 2866.00 | 2856.00 | 0.182 | 0.196 | 0.138 | 0.413 |
| `telepact_binary` | `all_numbers` | `really_big_list` | 32362.00 | 32352.00 | 0.300 | 0.535 | 1.224 | 3.897 |
| `telepact_packed_binary` | `typical_data` | `single` | 86.00 | 76.00 | 0.184 | 0.168 | 0.019 | 0.028 |
| `telepact_packed_binary` | `typical_data` | `small_list` | 505.00 | 495.00 | 0.162 | 0.179 | 0.088 | 0.113 |
| `telepact_packed_binary` | `typical_data` | `big_list` | 4789.00 | 4779.00 | 0.202 | 0.235 | 0.686 | 0.914 |
| `telepact_packed_binary` | `typical_data` | `really_big_list` | 47659.00 | 47649.00 | 0.387 | 0.606 | 6.628 | 9.129 |
| `telepact_packed_binary` | `all_strings` | `single` | 137.00 | 127.00 | 0.164 | 0.186 | 0.018 | 0.027 |
| `telepact_packed_binary` | `all_strings` | `small_list` | 1016.00 | 1006.00 | 0.144 | 0.157 | 0.078 | 0.109 |
| `telepact_packed_binary` | `all_strings` | `big_list` | 9748.00 | 9738.00 | 0.193 | 0.201 | 0.583 | 0.790 |
| `telepact_packed_binary` | `all_strings` | `really_big_list` | 97048.00 | 97038.00 | 0.452 | 0.883 | 5.629 | 7.774 |
| `telepact_packed_binary` | `all_numbers` | `single` | 62.00 | 52.00 | 0.153 | 0.180 | 0.018 | 0.031 |
| `telepact_packed_binary` | `all_numbers` | `small_list` | 266.00 | 256.00 | 0.146 | 0.176 | 0.089 | 0.118 |
| `telepact_packed_binary` | `all_numbers` | `big_list` | 2383.00 | 2373.00 | 0.202 | 0.213 | 0.593 | 0.810 |
| `telepact_packed_binary` | `all_numbers` | `really_big_list` | 27379.00 | 27369.00 | 0.346 | 0.549 | 5.696 | 7.763 |
| `protobuf` | `typical_data` | `single` | 50.00 | 50.00 | 0.155 | 0.171 | 0.001 | 0.004 |
| `protobuf` | `typical_data` | `small_list` | 509.00 | 509.00 | 0.155 | 0.153 | 0.002 | 0.005 |
| `protobuf` | `typical_data` | `big_list` | 5181.00 | 5181.00 | 0.186 | 0.194 | 0.008 | 0.016 |
| `protobuf` | `typical_data` | `really_big_list` | 51869.00 | 51869.00 | 0.226 | 0.208 | 0.055 | 0.064 |
| `protobuf` | `all_strings` | `single` | 105.00 | 105.00 | 0.154 | 0.161 | 0.001 | 0.003 |
| `protobuf` | `all_strings` | `small_list` | 1033.00 | 1033.00 | 0.175 | 0.160 | 0.002 | 0.004 |
| `protobuf` | `all_strings` | `big_list` | 10303.00 | 10303.00 | 0.185 | 0.162 | 0.007 | 0.010 |
| `protobuf` | `all_strings` | `really_big_list` | 103004.00 | 103004.00 | 0.253 | 0.315 | 0.048 | 0.062 |
| `protobuf` | `all_numbers` | `single` | 8.00 | 8.00 | 0.184 | 0.169 | 0.001 | 0.003 |
| `protobuf` | `all_numbers` | `small_list` | 243.00 | 243.00 | 0.164 | 0.150 | 0.002 | 0.004 |
| `protobuf` | `all_numbers` | `big_list` | 2694.00 | 2694.00 | 0.164 | 0.169 | 0.006 | 0.008 |
| `protobuf` | `all_numbers` | `really_big_list` | 28767.00 | 28767.00 | 0.169 | 0.202 | 0.040 | 0.042 |
| `plain_json` | `typical_data` | `single` | 124.00 | 124.00 | 0.157 | 0.150 | 0.008 | 0.007 |
| `plain_json` | `typical_data` | `small_list` | 1028.00 | 1028.00 | 0.166 | 0.160 | 0.018 | 0.016 |
| `plain_json` | `typical_data` | `big_list` | 10120.00 | 10120.00 | 0.173 | 0.154 | 0.096 | 0.089 |
| `plain_json` | `typical_data` | `really_big_list` | 101031.00 | 101031.00 | 0.317 | 0.537 | 0.797 | 0.795 |
| `plain_json` | `all_strings` | `single` | 175.00 | 175.00 | 0.147 | 0.147 | 0.006 | 0.007 |
| `plain_json` | `all_strings` | `small_list` | 1517.00 | 1517.00 | 0.131 | 0.143 | 0.013 | 0.014 |
| `plain_json` | `all_strings` | `big_list` | 14927.00 | 14927.00 | 0.145 | 0.170 | 0.066 | 0.055 |
| `plain_json` | `all_strings` | `really_big_list` | 149027.00 | 149027.00 | 0.364 | 0.559 | 0.536 | 0.515 |
| `plain_json` | `all_numbers` | `single` | 89.00 | 89.00 | 0.151 | 0.163 | 0.007 | 0.009 |
| `plain_json` | `all_numbers` | `small_list` | 742.00 | 742.00 | 0.137 | 0.141 | 0.017 | 0.018 |
| `plain_json` | `all_numbers` | `big_list` | 7618.00 | 7618.00 | 0.166 | 0.182 | 0.099 | 0.086 |
| `plain_json` | `all_numbers` | `really_big_list` | 81653.00 | 81653.00 | 0.272 | 0.246 | 0.942 | 0.836 |

## Typescript

| Method | Data shape | Collection shape | Req bytes mean | Resp bytes mean | Req transit p95 (ms) | Resp transit p95 (ms) | Client req serialize mean (ms) | Client resp deserialize mean (ms) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `telepact_json` | `typical_data` | `single` | 145.00 | 119.00 | 0.928 | 0.393 | 0.022 | 0.032 |
| `telepact_json` | `typical_data` | `small_list` | 1049.00 | 1025.00 | 0.249 | 0.240 | 0.023 | 0.017 |
| `telepact_json` | `typical_data` | `big_list` | 10141.00 | 10117.00 | 0.898 | 0.245 | 0.228 | 0.071 |
| `telepact_json` | `typical_data` | `really_big_list` | 101052.00 | 101028.00 | 0.508 | 1.051 | 0.566 | 0.487 |
| `telepact_json` | `all_strings` | `single` | 196.00 | 170.00 | 0.201 | 0.199 | 0.006 | 0.010 |
| `telepact_json` | `all_strings` | `small_list` | 1538.00 | 1514.00 | 0.194 | 0.183 | 0.010 | 0.014 |
| `telepact_json` | `all_strings` | `big_list` | 14948.00 | 14924.00 | 0.190 | 0.175 | 0.052 | 0.048 |
| `telepact_json` | `all_strings` | `really_big_list` | 149048.00 | 149024.00 | 1.151 | 1.307 | 0.572 | 0.497 |
| `telepact_json` | `all_numbers` | `single` | 106.00 | 80.00 | 0.170 | 0.153 | 0.009 | 0.011 |
| `telepact_json` | `all_numbers` | `small_list` | 757.00 | 733.00 | 0.184 | 0.172 | 0.010 | 0.015 |
| `telepact_json` | `all_numbers` | `big_list` | 7597.00 | 7573.00 | 0.186 | 0.183 | 0.047 | 0.060 |
| `telepact_json` | `all_numbers` | `really_big_list` | 81282.00 | 81258.00 | 0.474 | 0.775 | 0.428 | 0.321 |
| `telepact_binary` | `typical_data` | `single` | 81.00 | 71.00 | 0.178 | 0.194 | 0.087 | 0.031 |
| `telepact_binary` | `typical_data` | `small_list` | 549.00 | 539.00 | 0.221 | 0.237 | 0.053 | 0.059 |
| `telepact_binary` | `typical_data` | `big_list` | 5373.00 | 5363.00 | 0.259 | 0.279 | 0.606 | 0.154 |
| `telepact_binary` | `typical_data` | `really_big_list` | 53643.00 | 53633.00 | 0.282 | 0.900 | 2.479 | 0.669 |
| `telepact_binary` | `all_strings` | `single` | 132.00 | 122.00 | 0.165 | 0.174 | 0.015 | 0.034 |
| `telepact_binary` | `all_strings` | `small_list` | 1051.00 | 1041.00 | 0.145 | 0.159 | 0.046 | 0.022 |
| `telepact_binary` | `all_strings` | `big_list` | 10233.00 | 10223.00 | 0.206 | 0.913 | 0.373 | 0.100 |
| `telepact_binary` | `all_strings` | `really_big_list` | 102033.00 | 102023.00 | 1.273 | 1.026 | 0.929 | 0.453 |
| `telepact_binary` | `all_numbers` | `single` | 41.00 | 31.00 | 0.192 | 0.174 | 0.008 | 0.011 |
| `telepact_binary` | `all_numbers` | `small_list` | 277.00 | 267.00 | 0.162 | 0.170 | 0.027 | 0.015 |
| `telepact_binary` | `all_numbers` | `big_list` | 2705.00 | 2695.00 | 0.169 | 0.203 | 0.119 | 0.045 |
| `telepact_binary` | `all_numbers` | `really_big_list` | 30910.00 | 30900.00 | 0.888 | 0.826 | 1.096 | 0.391 |
| `telepact_packed_binary` | `typical_data` | `single` | 88.00 | 78.00 | 0.163 | 0.158 | 0.018 | 0.027 |
| `telepact_packed_binary` | `typical_data` | `small_list` | 507.00 | 497.00 | 0.164 | 0.179 | 0.057 | 0.045 |
| `telepact_packed_binary` | `typical_data` | `big_list` | 4791.00 | 4781.00 | 0.901 | 0.252 | 0.407 | 0.176 |
| `telepact_packed_binary` | `typical_data` | `really_big_list` | 47661.00 | 47651.00 | 1.288 | 0.286 | 2.189 | 0.600 |
| `telepact_packed_binary` | `all_strings` | `single` | 139.00 | 129.00 | 0.193 | 0.194 | 0.011 | 0.030 |
| `telepact_packed_binary` | `all_strings` | `small_list` | 1018.00 | 1008.00 | 0.190 | 0.210 | 0.024 | 0.024 |
| `telepact_packed_binary` | `all_strings` | `big_list` | 9750.00 | 9740.00 | 0.214 | 0.234 | 0.094 | 0.072 |
| `telepact_packed_binary` | `all_strings` | `really_big_list` | 97050.00 | 97040.00 | 0.368 | 1.248 | 0.664 | 0.466 |
| `telepact_packed_binary` | `all_numbers` | `single` | 48.00 | 38.00 | 0.169 | 0.165 | 0.011 | 0.017 |
| `telepact_packed_binary` | `all_numbers` | `small_list` | 244.00 | 234.00 | 0.183 | 0.163 | 0.022 | 0.025 |
| `telepact_packed_binary` | `all_numbers` | `big_list` | 2222.00 | 2212.00 | 0.157 | 0.160 | 0.055 | 0.057 |
| `telepact_packed_binary` | `all_numbers` | `really_big_list` | 25927.00 | 25917.00 | 0.745 | 0.743 | 0.423 | 0.356 |
| `protobuf` | `typical_data` | `single` | 50.00 | 50.00 | 0.155 | 0.160 | 0.029 | 0.054 |
| `protobuf` | `typical_data` | `small_list` | 509.00 | 509.00 | 0.175 | 0.218 | 0.057 | 0.043 |
| `protobuf` | `typical_data` | `big_list` | 5181.00 | 5181.00 | 0.272 | 0.247 | 0.714 | 0.242 |
| `protobuf` | `typical_data` | `really_big_list` | 51869.00 | 51869.00 | 0.536 | 0.936 | 0.939 | 0.730 |
| `protobuf` | `all_strings` | `single` | 105.00 | 105.00 | 1.280 | 0.278 | 0.010 | 0.042 |
| `protobuf` | `all_strings` | `small_list` | 1033.00 | 1033.00 | 0.151 | 0.164 | 0.013 | 0.025 |
| `protobuf` | `all_strings` | `big_list` | 10303.00 | 10303.00 | 0.216 | 0.230 | 0.126 | 0.172 |
| `protobuf` | `all_strings` | `really_big_list` | 103004.00 | 103004.00 | 0.429 | 0.928 | 0.669 | 1.113 |
| `protobuf` | `all_numbers` | `single` | 8.00 | 8.00 | 0.154 | 0.148 | 0.006 | 0.027 |
| `protobuf` | `all_numbers` | `small_list` | 243.00 | 243.00 | 0.159 | 0.147 | 0.019 | 0.037 |
| `protobuf` | `all_numbers` | `big_list` | 2694.00 | 2694.00 | 0.209 | 0.645 | 0.085 | 0.144 |
| `protobuf` | `all_numbers` | `really_big_list` | 28767.00 | 28767.00 | 0.622 | 0.363 | 0.592 | 0.415 |
| `plain_json` | `typical_data` | `single` | 124.00 | 124.00 | 0.163 | 0.174 | 0.006 | 0.010 |
| `plain_json` | `typical_data` | `small_list` | 1028.00 | 1028.00 | 0.175 | 0.165 | 0.018 | 0.017 |
| `plain_json` | `typical_data` | `big_list` | 10120.00 | 10120.00 | 0.183 | 0.152 | 0.045 | 0.061 |
| `plain_json` | `typical_data` | `really_big_list` | 101031.00 | 101031.00 | 0.361 | 0.434 | 0.373 | 0.442 |
| `plain_json` | `all_strings` | `single` | 175.00 | 175.00 | 0.177 | 0.162 | 0.005 | 0.007 |
| `plain_json` | `all_strings` | `small_list` | 1517.00 | 1517.00 | 0.159 | 0.170 | 0.010 | 0.013 |
| `plain_json` | `all_strings` | `big_list` | 14927.00 | 14927.00 | 0.187 | 0.198 | 0.043 | 0.048 |
| `plain_json` | `all_strings` | `really_big_list` | 149027.00 | 149027.00 | 0.857 | 0.318 | 0.429 | 0.440 |
| `plain_json` | `all_numbers` | `single` | 85.00 | 85.00 | 0.132 | 0.140 | 0.005 | 0.007 |
| `plain_json` | `all_numbers` | `small_list` | 736.00 | 736.00 | 0.194 | 0.174 | 0.011 | 0.012 |
| `plain_json` | `all_numbers` | `big_list` | 7576.00 | 7576.00 | 0.136 | 0.149 | 0.040 | 0.046 |
| `plain_json` | `all_numbers` | `really_big_list` | 81261.00 | 81261.00 | 0.446 | 0.382 | 0.377 | 0.301 |

## Java

| Method | Data shape | Collection shape | Req bytes mean | Resp bytes mean | Req transit p95 (ms) | Resp transit p95 (ms) | Client req serialize mean (ms) | Client resp deserialize mean (ms) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `telepact_json` | `typical_data` | `single` | 145.00 | 119.00 | 0.623 | 0.385 | 0.099 | 0.083 |
| `telepact_json` | `typical_data` | `small_list` | 1049.00 | 1025.00 | 0.340 | 1.559 | 0.207 | 0.118 |
| `telepact_json` | `typical_data` | `big_list` | 10141.00 | 10117.00 | 0.917 | 0.395 | 0.453 | 0.370 |
| `telepact_json` | `typical_data` | `really_big_list` | 101052.00 | 101028.00 | 0.778 | 1.431 | 2.250 | 1.409 |
| `telepact_json` | `all_strings` | `single` | 196.00 | 170.00 | 0.451 | 0.465 | 0.049 | 0.039 |
| `telepact_json` | `all_strings` | `small_list` | 1538.00 | 1514.00 | 0.272 | 0.331 | 0.056 | 0.048 |
| `telepact_json` | `all_strings` | `big_list` | 14948.00 | 14924.00 | 0.783 | 0.490 | 0.097 | 0.107 |
| `telepact_json` | `all_strings` | `really_big_list` | 149048.00 | 149024.00 | 1.350 | 0.744 | 0.535 | 0.530 |
| `telepact_json` | `all_numbers` | `single` | 110.00 | 84.00 | 0.301 | 0.270 | 0.034 | 0.040 |
| `telepact_json` | `all_numbers` | `small_list` | 763.00 | 739.00 | 0.209 | 1.230 | 0.052 | 0.042 |
| `telepact_json` | `all_numbers` | `big_list` | 7639.00 | 7615.00 | 0.542 | 0.284 | 0.137 | 0.111 |
| `telepact_json` | `all_numbers` | `really_big_list` | 81674.00 | 81650.00 | 0.939 | 0.570 | 0.823 | 0.603 |
| `telepact_binary` | `typical_data` | `single` | 79.00 | 69.00 | 0.296 | 0.363 | 0.096 | 0.098 |
| `telepact_binary` | `typical_data` | `small_list` | 547.00 | 537.00 | 0.242 | 0.299 | 0.218 | 0.210 |
| `telepact_binary` | `typical_data` | `big_list` | 5371.00 | 5361.00 | 0.382 | 0.338 | 0.783 | 0.698 |
| `telepact_binary` | `typical_data` | `really_big_list` | 53641.00 | 53631.00 | 0.482 | 0.542 | 2.802 | 2.606 |
| `telepact_binary` | `all_strings` | `single` | 130.00 | 120.00 | 0.242 | 0.729 | 0.052 | 0.046 |
| `telepact_binary` | `all_strings` | `small_list` | 1049.00 | 1039.00 | 0.208 | 0.599 | 0.086 | 0.083 |
| `telepact_binary` | `all_strings` | `big_list` | 10231.00 | 10221.00 | 0.242 | 0.298 | 0.253 | 0.311 |
| `telepact_binary` | `all_strings` | `really_big_list` | 102031.00 | 102021.00 | 0.511 | 0.448 | 2.613 | 1.062 |
| `telepact_binary` | `all_numbers` | `single` | 55.00 | 45.00 | 0.266 | 0.291 | 0.044 | 0.041 |
| `telepact_binary` | `all_numbers` | `small_list` | 299.00 | 289.00 | 0.253 | 0.349 | 0.059 | 0.068 |
| `telepact_binary` | `all_numbers` | `big_list` | 2866.00 | 2856.00 | 0.234 | 0.316 | 0.210 | 0.135 |
| `telepact_binary` | `all_numbers` | `really_big_list` | 32362.00 | 32352.00 | 0.307 | 0.485 | 0.851 | 0.950 |
| `telepact_packed_binary` | `typical_data` | `single` | 86.00 | 76.00 | 0.276 | 0.256 | 0.090 | 0.062 |
| `telepact_packed_binary` | `typical_data` | `small_list` | 505.00 | 495.00 | 1.393 | 0.437 | 0.146 | 0.112 |
| `telepact_packed_binary` | `typical_data` | `big_list` | 4789.00 | 4779.00 | 0.373 | 0.211 | 0.437 | 0.377 |
| `telepact_packed_binary` | `typical_data` | `really_big_list` | 47659.00 | 47649.00 | 0.319 | 0.335 | 2.130 | 3.235 |
| `telepact_packed_binary` | `all_strings` | `single` | 137.00 | 127.00 | 0.483 | 0.223 | 0.038 | 0.057 |
| `telepact_packed_binary` | `all_strings` | `small_list` | 1016.00 | 1006.00 | 0.846 | 0.979 | 0.090 | 0.067 |
| `telepact_packed_binary` | `all_strings` | `big_list` | 9748.00 | 9738.00 | 0.309 | 0.217 | 0.278 | 0.148 |
| `telepact_packed_binary` | `all_strings` | `really_big_list` | 97048.00 | 97038.00 | 0.654 | 0.923 | 1.206 | 0.881 |
| `telepact_packed_binary` | `all_numbers` | `single` | 62.00 | 52.00 | 0.186 | 0.168 | 0.025 | 0.030 |
| `telepact_packed_binary` | `all_numbers` | `small_list` | 266.00 | 256.00 | 0.175 | 0.345 | 0.050 | 0.055 |
| `telepact_packed_binary` | `all_numbers` | `big_list` | 2383.00 | 2373.00 | 0.159 | 0.173 | 0.151 | 0.108 |
| `telepact_packed_binary` | `all_numbers` | `really_big_list` | 27379.00 | 27369.00 | 0.270 | 0.358 | 0.981 | 0.453 |
| `protobuf` | `typical_data` | `single` | 50.00 | 50.00 | 0.270 | 0.587 | 0.016 | 0.119 |
| `protobuf` | `typical_data` | `small_list` | 509.00 | 509.00 | 0.189 | 0.225 | 0.072 | 0.446 |
| `protobuf` | `typical_data` | `big_list` | 5181.00 | 5181.00 | 0.308 | 1.278 | 0.232 | 1.578 |
| `protobuf` | `typical_data` | `really_big_list` | 51869.00 | 51869.00 | 0.333 | 0.329 | 0.626 | 3.798 |
| `protobuf` | `all_strings` | `single` | 105.00 | 105.00 | 0.229 | 0.158 | 0.003 | 0.029 |
| `protobuf` | `all_strings` | `small_list` | 1033.00 | 1033.00 | 0.174 | 0.356 | 0.006 | 0.072 |
| `protobuf` | `all_strings` | `big_list` | 10303.00 | 10303.00 | 0.178 | 0.226 | 0.024 | 0.245 |
| `protobuf` | `all_strings` | `really_big_list` | 103004.00 | 103004.00 | 0.419 | 0.350 | 0.212 | 1.352 |
| `protobuf` | `all_numbers` | `single` | 8.00 | 8.00 | 0.168 | 0.182 | 0.003 | 0.022 |
| `protobuf` | `all_numbers` | `small_list` | 243.00 | 243.00 | 0.161 | 0.173 | 0.004 | 0.029 |
| `protobuf` | `all_numbers` | `big_list` | 2694.00 | 2694.00 | 0.183 | 0.190 | 0.014 | 0.141 |
| `protobuf` | `all_numbers` | `really_big_list` | 28767.00 | 28767.00 | 0.228 | 0.228 | 0.107 | 0.816 |
| `plain_json` | `typical_data` | `single` | 124.00 | 124.00 | 0.154 | 0.172 | 0.013 | 0.046 |
| `plain_json` | `typical_data` | `small_list` | 1028.00 | 1028.00 | 0.180 | 0.210 | 0.021 | 0.040 |
| `plain_json` | `typical_data` | `big_list` | 10120.00 | 10120.00 | 0.168 | 0.172 | 0.080 | 0.153 |
| `plain_json` | `typical_data` | `really_big_list` | 101031.00 | 101031.00 | 0.944 | 0.359 | 0.707 | 1.208 |
| `plain_json` | `all_strings` | `single` | 175.00 | 175.00 | 0.756 | 0.207 | 0.016 | 0.039 |
| `plain_json` | `all_strings` | `small_list` | 1517.00 | 1517.00 | 0.188 | 0.203 | 0.017 | 0.049 |
| `plain_json` | `all_strings` | `big_list` | 14927.00 | 14927.00 | 0.418 | 1.041 | 0.071 | 0.108 |
| `plain_json` | `all_strings` | `really_big_list` | 149027.00 | 149027.00 | 0.705 | 0.405 | 0.564 | 0.627 |
| `plain_json` | `all_numbers` | `single` | 89.00 | 89.00 | 0.218 | 0.160 | 0.009 | 0.027 |
| `plain_json` | `all_numbers` | `small_list` | 742.00 | 742.00 | 0.131 | 0.153 | 0.018 | 0.025 |
| `plain_json` | `all_numbers` | `big_list` | 7618.00 | 7618.00 | 0.194 | 1.144 | 0.069 | 0.081 |
| `plain_json` | `all_numbers` | `really_big_list` | 81653.00 | 81653.00 | 0.680 | 0.543 | 0.640 | 0.642 |

