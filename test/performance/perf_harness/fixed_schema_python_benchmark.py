#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import msgpack

PERFORMANCE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PERFORMANCE_ROOT.parents[1]
sys.path.insert(0, str(REPO_ROOT / "lib" / "py"))

from telepact import TelepactSchema
from telepact.DefaultSerialization import DefaultSerialization
from telepact.internal.binary.ConstructBinaryEncoding import construct_binary_encoding
from telepact.internal.binary.ServerBinaryEncode import server_binary_encode

from perf_harness.common import FUNCTION_NAMES, PAYLOADS_PATH, SCHEMA_DIR


PACKED_EXT = msgpack.ExtType(17, b"")
UNDEFINED_EXT = msgpack.ExtType(18, b"")


def _legacy_encode_keys(value: object, encode_map: dict[str, int]) -> object:
    if type(value) is dict:
        return {
            encode_map.get(key, key) if type(key) is str else key: _legacy_encode_keys(item, encode_map)
            for key, item in value.items()
        }
    if type(value) is list:
        return [_legacy_encode_keys(item, encode_map) for item in value]
    return value


def _legacy_decode_keys(value: object, decode_table: list[str]) -> object:
    if type(value) is dict:
        decoded: dict[str, object] = {}
        for key, item in value.items():
            decoded_key = key if type(key) is str else decode_table[key]
            decoded[decoded_key] = _legacy_decode_keys(item, decode_table)
        return decoded
    if type(value) is list:
        return [_legacy_decode_keys(item, decode_table) for item in value]
    return value


def _legacy_pack(value: object) -> object:
    if type(value) is list:
        return _legacy_pack_list(value)
    if type(value) is dict:
        return {key: _legacy_pack(item) for key, item in value.items()}
    return value


def _legacy_pack_list(values: list[object]) -> list[object]:
    if not values:
        return values

    if any(type(value) is not dict for value in values):
        return [_legacy_pack(value) for value in values]

    header: list[object] = [None]
    key_index_map: dict[int, tuple[int, dict[int, Any]]] = {}
    rows: list[object] = [PACKED_EXT, header]

    try:
        for value in values:
            assert isinstance(value, dict)
            rows.append(_legacy_pack_map(value, header, key_index_map))
    except ValueError:
        return [_legacy_pack(value) for value in values]

    return rows


def _legacy_pack_map(
    value: dict[object, object],
    header: list[object],
    key_index_map: dict[int, tuple[int, dict[int, Any]]],
) -> list[object]:
    row: list[object] = [UNDEFINED_EXT] * (len(header) - 1)

    for raw_key, raw_value in value.items():
        if type(raw_key) is not int:
            raise ValueError("legacy packing requires encoded integer keys")

        key = raw_key
        node = key_index_map.get(key)
        if node is None:
            nested: dict[int, Any] = {}
            node = (len(header) - 1, nested)
            key_index_map[key] = node
            header.append([key] if type(raw_value) is dict else key)
            row.append(UNDEFINED_EXT)

        index, nested_map = node
        header_value = header[index + 1]

        if type(raw_value) is dict:
            if type(header_value) is not list:
                raise ValueError("legacy nested header mismatch")
            packed_value = _legacy_pack_map(raw_value, header_value, nested_map)
        else:
            if type(header_value) is list:
                raise ValueError("legacy scalar header mismatch")
            packed_value = _legacy_pack(raw_value) if type(raw_value) is list else raw_value

        row[index] = packed_value

    return row


def _legacy_unpack(value: object) -> object:
    if type(value) is list:
        return _legacy_unpack_list(value)
    if type(value) is dict:
        return {key: _legacy_unpack(item) for key, item in value.items()}
    return value


def _legacy_unpack_list(values: list[object]) -> list[object]:
    if not values:
        return values

    first_item = values[0]
    if type(first_item) is not msgpack.ExtType or first_item.code != 17:
        return [_legacy_unpack(item) for item in values]

    header = values[1]
    assert isinstance(header, list)
    return [
        _legacy_unpack_map(row, header)
        for row in values[2:]
        if isinstance(row, list)
    ]


def _legacy_unpack_map(row: list[object], header: list[object]) -> dict[int, object]:
    decoded: dict[int, object] = {}

    for index in range(min(len(row), len(header) - 1)):
        value = row[index]
        if type(value) is msgpack.ExtType and value.code == 18:
            continue

        header_entry = header[index + 1]
        if type(header_entry) is list:
            nested_header = header_entry
            assert isinstance(nested_header, list)
            decoded[nested_header[0]] = _legacy_unpack_map(value, nested_header)
        else:
            assert isinstance(header_entry, int)
            decoded[header_entry] = _legacy_unpack(value)

    return decoded


def _legacy_serialize(body: dict[str, object], headers: dict[str, object], binary_encoding: object) -> bytes:
    encoded_body = _legacy_encode_keys(body, binary_encoding.encode_map)
    packed_body = {key: _legacy_pack(value) for key, value in encoded_body.items()}
    return msgpack.dumps([headers, packed_body])


def _legacy_deserialize(payload: bytes, binary_encoding: object) -> dict[str, object]:
    decoded_message = msgpack.loads(payload, strict_map_key=False)
    unpacked_body = {key: _legacy_unpack(value) for key, value in decoded_message[1].items()}
    return _legacy_decode_keys(unpacked_body, binary_encoding.decode_table)


def _streaming_serialize(
    serializer: DefaultSerialization,
    body: dict[str, object],
    headers: dict[str, object],
    function_name: str,
    binary_encoding: object,
) -> bytes:
    encoded_message = server_binary_encode([
        {
            **headers,
            "@clientKnownBinaryChecksums_": [binary_encoding.checksum],
            "@binaryFunction_": function_name,
        },
        body,
    ], binary_encoding)
    return serializer.to_msgpack(encoded_message)


def _streaming_deserialize(
    serializer: DefaultSerialization,
    payload: bytes,
    function_name: str,
    binary_encoding: object,
) -> dict[str, object]:
    decoded_message = serializer.from_msgpack(payload)
    return DefaultSerialization.decode_binary_body(
        decoded_message[1],
        binary_encoding,
        binary_encoding.response_pack_trees[function_name],
    )


def _time_ns(iterations: int, warmup: int, fn) -> list[int]:
    for _ in range(warmup):
        fn()

    samples: list[int] = []
    for _ in range(iterations):
        started_at = time.perf_counter_ns()
        fn()
        samples.append(time.perf_counter_ns() - started_at)
    return samples


def _summary(samples: list[int]) -> dict[str, float]:
    return {
        "medianNs": statistics.median(samples),
        "meanNs": statistics.fmean(samples),
        "minNs": min(samples),
        "maxNs": max(samples),
    }


def _row(label: str, old_ns: float, new_ns: float) -> str:
    speedup = old_ns / new_ns if new_ns else 0.0
    return f"{label}: legacy={old_ns / 1_000_000:.3f}ms streaming={new_ns / 1_000_000:.3f}ms speedup={speedup:.2f}x"


def run_benchmark(iterations: int, warmup: int) -> dict[str, object]:
    schema = TelepactSchema.from_directory(str(SCHEMA_DIR))
    binary_encoding = construct_binary_encoding(schema)
    serializer = DefaultSerialization()
    payloads = json.loads(PAYLOADS_PATH.read_text())

    scenarios = []
    for data_shape, collection_shape in (
        ("typical", "big-list"),
        ("typical", "really-big-list"),
        ("all-strings", "really-big-list"),
        ("all-numbers", "really-big-list"),
    ):
        function_name = FUNCTION_NAMES[data_shape]
        body = {"Ok_": {"items": payloads[data_shape][collection_shape]}}
        headers = {"@pac_": True, "@bin_": [binary_encoding.checksum]}

        legacy_payload = _legacy_serialize(body, headers, binary_encoding)
        streaming_payload = _streaming_serialize(serializer, body, headers, function_name, binary_encoding)

        assert _legacy_deserialize(legacy_payload, binary_encoding) == body
        assert _streaming_deserialize(serializer, streaming_payload, function_name, binary_encoding) == body

        legacy_serialize = _time_ns(
            iterations,
            warmup,
            lambda: _legacy_serialize(body, headers, binary_encoding),
        )
        streaming_serialize = _time_ns(
            iterations,
            warmup,
            lambda: _streaming_serialize(serializer, body, headers, function_name, binary_encoding),
        )
        legacy_deserialize = _time_ns(
            iterations,
            warmup,
            lambda: _legacy_deserialize(legacy_payload, binary_encoding),
        )
        streaming_deserialize = _time_ns(
            iterations,
            warmup,
            lambda: _streaming_deserialize(serializer, streaming_payload, function_name, binary_encoding),
        )

        scenarios.append({
            "dataShape": data_shape,
            "collectionShape": collection_shape,
            "legacySizeBytes": len(legacy_payload),
            "streamingSizeBytes": len(streaming_payload),
            "legacySerialize": _summary(legacy_serialize),
            "streamingSerialize": _summary(streaming_serialize),
            "legacyDeserialize": _summary(legacy_deserialize),
            "streamingDeserialize": _summary(streaming_deserialize),
        })

    return {
        "iterations": iterations,
        "warmupIterations": warmup,
        "scenarios": scenarios,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=200)
    parser.add_argument("--warmup-iterations", type=int, default=25)
    parser.add_argument(
        "--output",
        type=Path,
        default=PERFORMANCE_ROOT / "results" / "fixed-schema-python.json",
    )
    args = parser.parse_args()

    results = run_benchmark(args.iterations, args.warmup_iterations)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2) + "\n")

    for scenario in results["scenarios"]:
        name = f"{scenario['dataShape']}/{scenario['collectionShape']}"
        print(_row(
            f"{name} serialize",
            scenario["legacySerialize"]["medianNs"],
            scenario["streamingSerialize"]["medianNs"],
        ))
        print(_row(
            f"{name} deserialize",
            scenario["legacyDeserialize"]["medianNs"],
            scenario["streamingDeserialize"]["medianNs"],
        ))
        size_delta = scenario["legacySizeBytes"] - scenario["streamingSizeBytes"]
        print(
            f"{name} size: legacy={scenario['legacySizeBytes']}B "
            f"streaming={scenario['streamingSizeBytes']}B saved={size_delta}B"
        )


if __name__ == "__main__":
    main()
