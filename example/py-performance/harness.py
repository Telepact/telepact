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

import argparse
import asyncio
import gc
import json
from dataclasses import dataclass
from statistics import mean, median
from time import perf_counter_ns
from typing import Callable

import msgpack
from msgpack import ExtType

from telepact import Client, Message, Serializer

from server import build_telepact_server

PACKED_BYTE = 17


@dataclass(frozen=True)
class Scenario:
    key: str
    title: str
    function_name: str
    select_header: dict[str, object]


@dataclass(frozen=True)
class NetworkProfile:
    key: str
    title: str
    distance_km: int
    bandwidth_mbps: float
    round_trip_ms: float


@dataclass
class CallSample:
    serialize_ns: int
    deserialize_ns: int
    roundtrip_ns: int
    request_bytes: int
    response_bytes: int
    request_wire_mode: str
    response_wire_mode: str
    saw_negotiation: bool


SCENARIOS = [
    Scenario(
        key='flat_numbers',
        title='Flat numbers',
        function_name='fn.getFlatNumbers',
        select_header={
            '->': {'Ok_': ['value']},
            'struct.FlatNumbers': ['value01', 'value02', 'value03', 'value04', 'value05', 'value06'],
        },
    ),
    Scenario(
        key='flat_strings',
        title='Flat strings',
        function_name='fn.getFlatStrings',
        select_header={
            '->': {'Ok_': ['value']},
            'struct.FlatStrings': ['value01', 'value02', 'value03', 'value04', 'value05', 'value06'],
        },
    ),
    Scenario(
        key='record_batch',
        title='List of structs',
        function_name='fn.getRecordBatch',
        select_header={
            '->': {'Ok_': ['rows', 'summary']},
            'struct.Record': ['recordId', 'status', 'score'],
            'struct.RecordSummary': ['totalRows', 'totalScore'],
        },
    ),
    Scenario(
        key='dashboard',
        title='Typical dashboard',
        function_name='fn.getDashboard',
        select_header={
            '->': {'Ok_': ['profile', 'orders', 'metrics']},
            'struct.Profile': ['accountId', 'plan', 'region'],
            'struct.Order': ['orderId', 'status', 'total', 'lines'],
            'struct.OrderLine': ['sku', 'quantity'],
            'struct.DashboardMetrics': ['monthlySpend', 'activeUsers', 'latencyP95Ms'],
        },
    ),
]

NETWORK_PROFILES = [
    NetworkProfile('lan', 'Office LAN (~1 km)', 1, 1000, 2.0),
    NetworkProfile('metro_wifi', 'Metro Wi-Fi (~50 km)', 50, 200, 8.0),
    NetworkProfile('regional_4g', 'Regional 4G (~500 km)', 500, 20, 55.0),
    NetworkProfile('cross_country', 'Cross-country broadband (~4,000 km)', 4000, 100, 70.0),
    NetworkProfile('intercontinental', 'Intercontinental broadband (~9,000 km)', 9000, 50, 150.0),
]


def _is_json_wire(message_bytes: bytes) -> bool:
    stripped = message_bytes.lstrip()
    return stripped.startswith(b'[') or stripped.startswith(b'{')


def _contains_packed_binary(value: object) -> bool:
    if isinstance(value, ExtType):
        return value.code == PACKED_BYTE
    if isinstance(value, list):
        return any(_contains_packed_binary(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_packed_binary(item) for item in value.values())
    return False


def classify_wire_mode(message_bytes: bytes) -> str:
    if _is_json_wire(message_bytes):
        return 'json'
    unpacked = msgpack.unpackb(message_bytes, raw=False, strict_map_key=False)
    if _contains_packed_binary(unpacked):
        return 'packed-binary'
    return 'binary'


def _format_us(ns: float) -> float:
    return round(ns / 1_000, 2)


def _estimate_total_network_latency_ms(total_bytes: float, profile: NetworkProfile) -> float:
    transfer_ms = (total_bytes * 8) / (profile.bandwidth_mbps * 1_000_000) * 1_000
    return round(profile.round_trip_ms + transfer_ms, 3)


def _build_request(scenario: Scenario, size: str, use_select: bool, use_unsafe: bool) -> Message:
    headers: dict[str, object] = {}
    if use_select:
        headers['@select_'] = json.loads(json.dumps(scenario.select_header))
    if use_unsafe:
        headers['@unsafe_'] = True
    return Message(headers, {scenario.function_name: {'size': size}})


def _build_client(use_binary: bool) -> tuple[Client, list[CallSample]]:
    server = build_telepact_server()
    samples: list[CallSample] = []

    async def adapter(message: Message, serializer: Serializer) -> Message:
        start_ns = perf_counter_ns()
        serialize_start_ns = perf_counter_ns()
        request_bytes = serializer.serialize(message)
        serialize_ns = perf_counter_ns() - serialize_start_ns

        response = await server.process(request_bytes)

        deserialize_start_ns = perf_counter_ns()
        decoded = serializer.deserialize(response.bytes)
        deserialize_ns = perf_counter_ns() - deserialize_start_ns
        roundtrip_ns = perf_counter_ns() - start_ns

        samples.append(CallSample(
            serialize_ns=serialize_ns,
            deserialize_ns=deserialize_ns,
            roundtrip_ns=roundtrip_ns,
            request_bytes=len(request_bytes),
            response_bytes=len(response.bytes),
            request_wire_mode=classify_wire_mode(request_bytes),
            response_wire_mode=classify_wire_mode(response.bytes),
            saw_negotiation='@enc_' in response.headers,
        ))
        return decoded

    options = Client.Options()
    options.use_binary = use_binary
    options.always_send_json = not use_binary
    return Client(adapter, options), samples


async def _measure_permutation(
    scenario: Scenario,
    size: str,
    use_binary: bool,
    use_packed: bool,
    use_select: bool,
    use_unsafe: bool,
    cycles: int,
    steady_state_warmup: int,
) -> dict[str, object]:
    client, samples = _build_client(use_binary)
    measured_samples: list[CallSample] = []
    steady_samples_seen = 0
    attempts = 0
    max_attempts = cycles + steady_state_warmup + 8

    while len(measured_samples) < cycles:
        message = _build_request(scenario, size, use_select, use_unsafe)
        if use_binary and use_packed:
            message.headers['@pac_'] = True
        await client.request(message)
        sample = samples[-1]
        attempts += 1
        if attempts > max_attempts:
            raise RuntimeError('Timed out waiting for steady-state benchmark samples')

        if use_binary and (
            sample.saw_negotiation
            or sample.request_wire_mode == 'json'
            or sample.response_wire_mode == 'json'
        ):
            continue

        if steady_samples_seen < steady_state_warmup:
            steady_samples_seen += 1
            continue

        measured_samples.append(sample)

    serialize_ns = [sample.serialize_ns for sample in measured_samples]
    deserialize_ns = [sample.deserialize_ns for sample in measured_samples]
    roundtrip_ns = [sample.roundtrip_ns for sample in measured_samples]
    request_bytes = [sample.request_bytes for sample in measured_samples]
    response_bytes = [sample.response_bytes for sample in measured_samples]
    total_bytes_mean = mean(request_bytes) + mean(response_bytes)
    response_wire_modes = {sample.response_wire_mode for sample in measured_samples}
    if len(response_wire_modes) != 1:
        raise RuntimeError(f'Expected one steady-state response wire mode, got {sorted(response_wire_modes)}')

    return {
        'scenario': scenario.key,
        'scenario_title': scenario.title,
        'size': size,
        'client_mode': 'binary' if use_binary else 'json',
        'use_packed': use_packed,
        'steady_state_wire_mode': next(iter(response_wire_modes)),
        'use_select': use_select,
        'use_unsafe': use_unsafe,
        'steady_state_samples': len(measured_samples),
        'discarded_handshake_samples': len(samples) - len(measured_samples) - steady_state_warmup,
        'steady_state_handshake_seen': any(sample.saw_negotiation for sample in measured_samples),
        'median_serialize_us': _format_us(median(serialize_ns)),
        'median_deserialize_us': _format_us(median(deserialize_ns)),
        'median_roundtrip_us': _format_us(median(roundtrip_ns)),
        'mean_request_bytes': round(mean(request_bytes), 2),
        'mean_response_bytes': round(mean(response_bytes), 2),
        'mean_total_bytes': round(total_bytes_mean, 2),
        'network_latency_ms': {
            profile.key: _estimate_total_network_latency_ms(total_bytes_mean, profile)
            for profile in NETWORK_PROFILES
        },
    }


def _measurement_sort_key(row: dict[str, object]) -> tuple[object, ...]:
    return (
        row['scenario'],
        row['size'],
        row['client_mode'],
        row['use_packed'],
        row['use_select'],
        row['use_unsafe'],
    )


def _render_table(rows: list[dict[str, object]], columns: list[tuple[str, str]]) -> str:
    widths = {
        key: max(len(title), *(len(str(row[key])) for row in rows))
        for key, title in columns
    }
    header = ' | '.join(title.ljust(widths[key]) for key, title in columns)
    divider = '-|-'.join('-' * widths[key] for key, _title in columns)
    body = [
        ' | '.join(str(row[key]).ljust(widths[key]) for key, _title in columns)
        for row in rows
    ]
    return '\n'.join([header, divider, *body])


def _build_recommendations(measurements: list[dict[str, object]]) -> list[str]:
    recommendations: list[str] = []

    grouped: dict[tuple[str, str], list[dict[str, object]]] = {}
    for measurement in measurements:
        grouped.setdefault((measurement['scenario'], measurement['size']), []).append(measurement)

    for (scenario, size), rows in sorted(grouped.items()):
        baseline = next(
            row for row in rows
            if row['client_mode'] == 'json' and not row['use_packed'] and not row['use_select'] and not row['use_unsafe']
        )
        smallest = min(rows, key=lambda row: row['mean_total_bytes'])
        if smallest['mean_total_bytes'] < baseline['mean_total_bytes']:
            savings_pct = round((1 - (smallest['mean_total_bytes'] / baseline['mean_total_bytes'])) * 100, 1)
            recommendations.append(
                f'{scenario}/{size}: prefer {smallest["client_mode"]} with '
                f'{"@pac_ + " if smallest["use_packed"] else ""}'
                f'{"@select_ + " if smallest["use_select"] else ""}'
                f'{"@unsafe_ + " if smallest["use_unsafe"] else ""}'
                f'{smallest["steady_state_wire_mode"]} when link bandwidth matters; '
                f'total bytes dropped by {savings_pct}% vs JSON.'
            )

        packed_rows = [row for row in rows if row['steady_state_wire_mode'] == 'packed-binary']
        if packed_rows:
            best_packed = min(packed_rows, key=lambda row: row['mean_total_bytes'])
            savings_pct = round((1 - (best_packed['mean_total_bytes'] / baseline['mean_total_bytes'])) * 100, 1)
            recommendations.append(
                f'{scenario}/{size}: enable @pac_ for list-heavy responses; '
                f'that saved {savings_pct}% vs JSON in this harness.'
            )

        safe_rows = {
            (row['client_mode'], row['use_packed'], row['use_select']): row
            for row in rows
            if not row['use_unsafe']
        }
        for row in rows:
            if not row['use_unsafe']:
                continue
            peer = safe_rows.get((row['client_mode'], row['use_packed'], row['use_select']))
            if peer is None:
                continue
            if row['median_roundtrip_us'] < peer['median_roundtrip_us']:
                reduction_pct = round((1 - (row['median_roundtrip_us'] / peer['median_roundtrip_us'])) * 100, 1)
                recommendations.append(
                    f'{scenario}/{size}: on trusted hot paths, @unsafe_ cut local steady-state '
                    f'round-trip latency by {reduction_pct}% for {row["client_mode"]} mode.'
                )
                break

    recommendations.append(
        'Use @select_ first for UI-style partial reads: it shrinks both JSON and binary payloads, '
        'which compounds with slower or longer-distance networks.'
    )
    recommendations.append(
        'Use runtime binary for steady-state caller/server pairs that exchange more than tiny payloads; '
        'the handshake cost is one-time and excluded from the steady-state measurements here.'
    )
    return recommendations


async def run_benchmark(cycles: int = 80, steady_state_warmup: int = 4) -> dict[str, object]:
    measurements: list[dict[str, object]] = []
    gc_enabled = gc.isenabled()
    gc.disable()
    try:
        for scenario in SCENARIOS:
            for size in ['small', 'big']:
                for use_binary in [False, True]:
                    packed_options = [False, True] if use_binary else [False]
                    for use_packed in packed_options:
                        for use_select in [False, True]:
                            for use_unsafe in [False, True]:
                                measurements.append(await _measure_permutation(
                                    scenario=scenario,
                                    size=size,
                                    use_binary=use_binary,
                                    use_packed=use_packed,
                                    use_select=use_select,
                                    use_unsafe=use_unsafe,
                                    cycles=cycles,
                                    steady_state_warmup=steady_state_warmup,
                                ))
    finally:
        if gc_enabled:
            gc.enable()

    measurements.sort(key=_measurement_sort_key)
    return {
        'cycles': cycles,
        'steady_state_warmup': steady_state_warmup,
        'measurements': measurements,
        'recommendations': _build_recommendations(measurements),
    }


def render_report(report: dict[str, object]) -> str:
    measurements = report['measurements']
    measurement_rows = [{
        'scenario': row['scenario'],
        'size': row['size'],
        'mode': row['client_mode'],
        'packed': row['use_packed'],
        'wire': row['steady_state_wire_mode'],
        'select': row['use_select'],
        'unsafe': row['use_unsafe'],
        'ser_us': row['median_serialize_us'],
        'deser_us': row['median_deserialize_us'],
        'rt_us': row['median_roundtrip_us'],
        'req_b': row['mean_request_bytes'],
        'res_b': row['mean_response_bytes'],
        'total_b': row['mean_total_bytes'],
        'discarded': row['discarded_handshake_samples'],
    } for row in measurements]

    network_rows = []
    for row in measurements:
        network_row = {
            'scenario': row['scenario'],
            'size': row['size'],
            'mode': row['client_mode'],
            'packed': row['use_packed'],
            'wire': row['steady_state_wire_mode'],
            'select': row['use_select'],
            'unsafe': row['use_unsafe'],
        }
        network_row.update(row['network_latency_ms'])
        network_rows.append(network_row)

    return '\n'.join([
        '# Telepact Python performance harness',
        '',
        'Steady-state metrics only. Binary handshake/negotiation samples are discarded before measurement.',
        f'Samples per permutation: {report["cycles"]} (steady-state warmup after negotiation: {report["steady_state_warmup"]})',
        '',
        '## Measurements',
        _render_table(measurement_rows, [
            ('scenario', 'scenario'),
            ('size', 'size'),
            ('mode', 'client'),
            ('packed', '@pac_'),
            ('wire', 'wire'),
            ('select', '@select_'),
            ('unsafe', '@unsafe_'),
            ('ser_us', 'ser µs'),
            ('deser_us', 'deser µs'),
            ('rt_us', 'roundtrip µs'),
            ('req_b', 'req bytes'),
            ('res_b', 'res bytes'),
            ('total_b', 'total bytes'),
            ('discarded', 'discarded'),
        ]),
        '',
        '## Estimated network latency from measured payload sizes (request + response)',
        _render_table(network_rows, [
            ('scenario', 'scenario'),
            ('size', 'size'),
            ('mode', 'client'),
            ('packed', '@pac_'),
            ('wire', 'wire'),
            ('select', '@select_'),
            ('unsafe', '@unsafe_'),
            ('lan', 'LAN ms'),
            ('metro_wifi', 'Metro ms'),
            ('regional_4g', '4G ms'),
            ('cross_country', 'Cross-country ms'),
            ('intercontinental', 'Intercontinental ms'),
        ]),
        '',
        '## Recommendations',
        *[f'- {recommendation}' for recommendation in report['recommendations']],
    ])


def run_benchmark_sync(cycles: int = 80, steady_state_warmup: int = 4) -> dict[str, object]:
    return asyncio.run(run_benchmark(cycles=cycles, steady_state_warmup=steady_state_warmup))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Run the Telepact Python performance harness.')
    parser.add_argument('--cycles', type=int, default=80, help='Steady-state samples to collect per permutation.')
    parser.add_argument('--steady-state-warmup', type=int, default=4, help='Extra steady-state warmup samples to discard after negotiation.')
    args = parser.parse_args(argv)

    report = run_benchmark_sync(cycles=args.cycles, steady_state_warmup=args.steady_state_warmup)
    print(render_report(report))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
