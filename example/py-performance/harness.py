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
TREND_ROW_COUNTS = [8, 16, 32, 64, 128, 192, 256, 384]
TREND_SIZE = 'big'
SVG_SERIES_COLORS = {
    'typical_json': '#6b7280',
    'typical_binary': '#2563eb',
    'typical_packed_binary': '#1d4ed8',
    'integers_json': '#9ca3af',
    'integers_binary': '#ea580c',
    'integers_packed_binary': '#c2410c',
}


@dataclass(frozen=True)
class Scenario:
    key: str
    title: str
    function_name: str
    select_header: dict[str, object]
    supports_row_count: bool = False


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
        supports_row_count=True,
    ),
    Scenario(
        key='integer_row_batch',
        title='Integer-only list of structs',
        function_name='fn.getIntegerRowBatch',
        select_header={
            '->': {'Ok_': ['rows', 'summary']},
            'struct.IntegerRow': ['col01', 'col02', 'col03', 'col04'],
            'struct.IntegerRowSummary': ['totalRows', 'maxValue'],
        },
        supports_row_count=True,
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


def _default_row_count(scenario: Scenario, size: str) -> int:
    if scenario.key == 'record_batch':
        return 10 if size == 'small' else 120
    if scenario.key == 'integer_row_batch':
        return 30 if size == 'small' else 360
    raise ValueError(f'Scenario does not support row count defaults: {scenario.key}')


def _build_request(
    scenario: Scenario,
    size: str,
    use_select: bool,
    use_unsafe: bool,
    row_count: int | None = None,
) -> Message:
    headers: dict[str, object] = {}
    if use_select:
        headers['@select_'] = json.loads(json.dumps(scenario.select_header))
    if use_unsafe:
        headers['@unsafe_'] = True
    request_body: dict[str, object] = {'size': size}
    if scenario.supports_row_count:
        request_body['rowCount'] = row_count if row_count is not None else _default_row_count(scenario, size)
    return Message(headers, {scenario.function_name: request_body})


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
    row_count: int | None = None,
) -> dict[str, object]:
    client, samples = _build_client(use_binary)
    measured_samples: list[CallSample] = []
    steady_samples_seen = 0
    attempts = 0
    max_attempts = cycles + steady_state_warmup + 8

    while len(measured_samples) < cycles:
        message = _build_request(scenario, size, use_select, use_unsafe, row_count=row_count)
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
        'row_count': row_count,
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


def _format_pct(value: float) -> float:
    return round(value, 1)


def _pct_change(new_value: float, old_value: float) -> float:
    if old_value == 0:
        return 0.0
    return ((new_value / old_value) - 1) * 100


def _payload_reduction_pct(new_value: float, baseline: float) -> float:
    if baseline == 0:
        return 0.0
    return (1 - (new_value / baseline)) * 100


def _series_key(scenario_key: str, client_mode: str, use_packed: bool) -> str:
    family = 'typical' if scenario_key == 'record_batch' else 'integers'
    mode = 'packed_binary' if use_packed else client_mode
    return f'{family}_{mode}'


def _series_title(series_key: str) -> str:
    return {
        'typical_json': 'Typical JSON',
        'typical_binary': 'Typical binary',
        'typical_packed_binary': 'Typical packed binary',
        'integers_json': 'Integers JSON',
        'integers_binary': 'Integers binary',
        'integers_packed_binary': 'Integers packed binary',
    }[series_key]


def _solve_linear_system(matrix: list[list[float]], vector: list[float]) -> list[float]:
    size = len(vector)
    augmented = [row[:] + [value] for row, value in zip(matrix, vector, strict=True)]
    for pivot_index in range(size):
        pivot_row = max(range(pivot_index, size), key=lambda row_index: abs(augmented[row_index][pivot_index]))
        augmented[pivot_index], augmented[pivot_row] = augmented[pivot_row], augmented[pivot_index]
        pivot = augmented[pivot_index][pivot_index]
        if abs(pivot) < 1e-12:
            raise ValueError('Singular matrix')
        for column_index in range(pivot_index, size + 1):
            augmented[pivot_index][column_index] /= pivot
        for row_index in range(size):
            if row_index == pivot_index:
                continue
            factor = augmented[row_index][pivot_index]
            for column_index in range(pivot_index, size + 1):
                augmented[row_index][column_index] -= factor * augmented[pivot_index][column_index]
    return [augmented[row_index][-1] for row_index in range(size)]


def _fit_quadratic_regression(xs: list[int], ys: list[float]) -> tuple[float, float, float, int, int]:
    min_x = min(xs)
    max_x = max(xs)
    span = max(max_x - min_x, 1)
    normalized_xs = [(x - min_x) / span for x in xs]
    s0 = len(xs)
    s1 = sum(normalized_xs)
    s2 = sum(x ** 2 for x in normalized_xs)
    s3 = sum(x ** 3 for x in normalized_xs)
    s4 = sum(x ** 4 for x in normalized_xs)
    sy = sum(ys)
    sxy = sum(x * y for x, y in zip(normalized_xs, ys, strict=True))
    sx2y = sum((x ** 2) * y for x, y in zip(normalized_xs, ys, strict=True))
    try:
        a, b, c = _solve_linear_system(
            [
                [s0, s1, s2],
                [s1, s2, s3],
                [s2, s3, s4],
            ],
            [sy, sxy, sx2y],
        )
    except ValueError:
        a = mean(ys)
        b = 0.0
        c = 0.0
    return a, b, c, min_x, span


def _evaluate_quadratic_regression(coefficients: tuple[float, float, float, int, int], x: float) -> float:
    a, b, c, min_x, span = coefficients
    normalized_x = (x - min_x) / span
    return a + (b * normalized_x) + (c * (normalized_x ** 2))


def _build_trend_regressions(trend_measurements: list[dict[str, object]], steps: int = 40) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in trend_measurements:
        grouped.setdefault(row['series_key'], []).append(row)

    regressions: list[dict[str, object]] = []
    for series_key, rows in sorted(grouped.items()):
        sorted_rows = sorted(rows, key=lambda row: row['list_size'])
        xs = [int(row['list_size']) for row in sorted_rows]
        ys = [float(row['payload_reduction_pct']) for row in sorted_rows]
        coefficients = _fit_quadratic_regression(xs, ys)
        min_x = min(xs)
        max_x = max(xs)
        if max_x == min_x:
            curve_xs = [float(min_x)]
        else:
            curve_xs = [min_x + ((max_x - min_x) * step / (steps - 1)) for step in range(steps)]
        regressions.append({
            'series_key': series_key,
            'series_title': _series_title(series_key),
            'curve_points': [{
                'list_size': round(x_value, 2),
                'payload_reduction_pct': _format_pct(min(100.0, max(0.0, _evaluate_quadratic_regression(coefficients, x_value)))),
            } for x_value in curve_xs],
        })
    return regressions


def _build_trend_measurements(
    measurements: list[dict[str, object]],
    trend_measurements: list[dict[str, object]],
) -> list[dict[str, object]]:
    del measurements
    return sorted(trend_measurements, key=lambda row: (row['series_key'], row['list_size']))


def _build_timing_tradeoffs(measurements: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in measurements:
        grouped.setdefault((row['scenario'], row['size']), []).append(row)

    rows: list[dict[str, object]] = []
    technique_specs = [
        ('@select_', {'client_mode': 'json', 'use_packed': False, 'use_select': True, 'use_unsafe': False}),
        ('binary', {'client_mode': 'binary', 'use_packed': False, 'use_select': False, 'use_unsafe': False}),
        ('@pac_ (binary)', {'client_mode': 'binary', 'use_packed': True, 'use_select': False, 'use_unsafe': False}),
        ('@unsafe_', {'client_mode': 'json', 'use_packed': False, 'use_select': False, 'use_unsafe': True}),
    ]
    for (scenario, size), scenario_rows in sorted(grouped.items()):
        baseline = next(
            row for row in scenario_rows
            if row['client_mode'] == 'json' and not row['use_packed'] and not row['use_select'] and not row['use_unsafe']
        )
        for technique, criteria in technique_specs:
            candidate = next(row for row in scenario_rows if all(row[key] == value for key, value in criteria.items()))
            serialize_change_pct = _format_pct(_pct_change(candidate['median_serialize_us'], baseline['median_serialize_us']))
            deserialize_change_pct = _format_pct(_pct_change(candidate['median_deserialize_us'], baseline['median_deserialize_us']))
            payload_reduction_pct = _format_pct(_payload_reduction_pct(candidate['mean_total_bytes'], baseline['mean_total_bytes']))
            rows.append({
                'scenario': scenario,
                'size': size,
                'technique': technique,
                'payload_reduction_pct': payload_reduction_pct,
                'serialize_change_pct': serialize_change_pct,
                'deserialize_change_pct': deserialize_change_pct,
                'serialize_note': 'slower' if serialize_change_pct > 3 else 'faster' if serialize_change_pct < -3 else 'about even',
                'deserialize_note': 'slower' if deserialize_change_pct > 3 else 'faster' if deserialize_change_pct < -3 else 'about even',
            })
    return rows


def _render_payload_reduction_svg(
    trend_measurements: list[dict[str, object]],
    trend_regressions: list[dict[str, object]],
) -> str:
    width = 920
    height = 560
    margin_left = 90
    margin_right = 30
    margin_top = 40
    margin_bottom = 80
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    x_values = [int(row['list_size']) for row in trend_measurements]
    x_ticks = sorted(set(x_values))
    x_min = min(x_values)
    x_max = max(x_values)
    y_min = 0
    y_max = 100

    def x_to_svg(x_value: float) -> float:
        if x_max == x_min:
            return margin_left + (plot_width / 2)
        return margin_left + ((x_value - x_min) / (x_max - x_min) * plot_width)

    def y_to_svg(y_value: float) -> float:
        return margin_top + ((y_max - y_value) / (y_max - y_min) * plot_height)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Payload reduction percent by list size">',
        '<style>',
        'text { font-family: Arial, sans-serif; font-size: 12px; fill: #111827; }',
        '.axis { stroke: #111827; stroke-width: 1; }',
        '.grid { stroke: #e5e7eb; stroke-width: 1; }',
        '.series-line { fill: none; stroke-width: 2.5; }',
        '.series-point { stroke: white; stroke-width: 1.5; }',
        '</style>',
    ]

    for y_tick in [0, 20, 40, 60, 80, 100]:
        y_svg = y_to_svg(y_tick)
        parts.append(f'<line class="grid" x1="{margin_left}" y1="{y_svg}" x2="{width - margin_right}" y2="{y_svg}" />')
        parts.append(f'<text x="{margin_left - 12}" y="{y_svg + 4}" text-anchor="end">{y_tick}%</text>')
    for x_tick in x_ticks:
        x_svg = x_to_svg(x_tick)
        parts.append(f'<line class="grid" x1="{x_svg}" y1="{margin_top}" x2="{x_svg}" y2="{height - margin_bottom}" />')
        parts.append(f'<text x="{x_svg}" y="{height - margin_bottom + 22}" text-anchor="middle">{x_tick}</text>')

    parts.append(f'<line class="axis" x1="{margin_left}" y1="{height - margin_bottom}" x2="{width - margin_right}" y2="{height - margin_bottom}" />')
    parts.append(f'<line class="axis" x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{height - margin_bottom}" />')
    parts.append(f'<text x="{width / 2}" y="{height - 20}" text-anchor="middle">List size (rows)</text>')
    parts.append(f'<text x="24" y="{height / 2}" transform="rotate(-90 24 {height / 2})" text-anchor="middle">Payload reduction percent</text>')

    grouped_points: dict[str, list[dict[str, object]]] = {}
    for row in trend_measurements:
        grouped_points.setdefault(row['series_key'], []).append(row)

    for regression in trend_regressions:
        color = SVG_SERIES_COLORS[regression['series_key']]
        points_attr = ' '.join(
            f'{x_to_svg(float(point["list_size"])):.2f},{y_to_svg(float(point["payload_reduction_pct"])):.2f}'
            for point in regression['curve_points']
        )
        parts.append(f'<polyline class="series-line" stroke="{color}" points="{points_attr}" />')

    for series_key, rows in sorted(grouped_points.items()):
        color = SVG_SERIES_COLORS[series_key]
        for row in sorted(rows, key=lambda item: item['list_size']):
            parts.append(
                f'<circle class="series-point" cx="{x_to_svg(float(row["list_size"])):.2f}" '
                f'cy="{y_to_svg(float(row["payload_reduction_pct"])):.2f}" r="4" fill="{color}" />'
            )

    legend_x = margin_left + 10
    legend_y = 18
    for index, series_key in enumerate([
        'typical_json',
        'typical_binary',
        'typical_packed_binary',
        'integers_json',
        'integers_binary',
        'integers_packed_binary',
    ]):
        x_offset = legend_x + ((index % 3) * 245)
        y_offset = legend_y + ((index // 3) * 18)
        color = SVG_SERIES_COLORS[series_key]
        parts.append(f'<line class="series-line" stroke="{color}" x1="{x_offset}" y1="{y_offset}" x2="{x_offset + 24}" y2="{y_offset}" />')
        parts.append(f'<circle class="series-point" cx="{x_offset + 12}" cy="{y_offset}" r="4" fill="{color}" />')
        parts.append(f'<text x="{x_offset + 32}" y="{y_offset + 4}">{_series_title(series_key)}</text>')

    parts.append('</svg>')
    return '\n'.join(parts)


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
    recommendations.append(
        'Large integer-only row batches are the strongest @pac_ case in this harness: repeated field names disappear, '
        'so packed binary can dramatically outperform both JSON and non-packed binary.'
    )
    return recommendations


async def run_benchmark(
    cycles: int = 80,
    steady_state_warmup: int = 4,
    trend_cycles: int | None = None,
    trend_row_counts: list[int] | None = None,
) -> dict[str, object]:
    measurements: list[dict[str, object]] = []
    trend_rows: list[dict[str, object]] = []
    trend_cycles = trend_cycles if trend_cycles is not None else max(4, min(cycles, 8))
    trend_row_counts = trend_row_counts if trend_row_counts is not None else TREND_ROW_COUNTS
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
        trend_scenarios = [scenario for scenario in SCENARIOS if scenario.key in ['record_batch', 'integer_row_batch']]
        for scenario in trend_scenarios:
            for row_count in trend_row_counts:
                scenario_trend_rows: list[dict[str, object]] = []
                for use_binary in [False, True]:
                    packed_options = [False, True] if use_binary else [False]
                    for use_packed in packed_options:
                        scenario_trend_rows.append(await _measure_permutation(
                            scenario=scenario,
                            size=TREND_SIZE,
                            row_count=row_count,
                            use_binary=use_binary,
                            use_packed=use_packed,
                            use_select=False,
                            use_unsafe=False,
                            cycles=trend_cycles,
                            steady_state_warmup=steady_state_warmup,
                        ))
                baseline = next(row for row in scenario_trend_rows if row['client_mode'] == 'json')
                for row in scenario_trend_rows:
                    row['family'] = 'typical' if scenario.key == 'record_batch' else 'integers'
                    row['list_size'] = row_count
                    row['series_key'] = _series_key(scenario.key, row['client_mode'], row['use_packed'])
                    row['series_title'] = _series_title(row['series_key'])
                    row['payload_reduction_pct'] = _format_pct(
                        _payload_reduction_pct(row['mean_total_bytes'], baseline['mean_total_bytes'])
                    )
                    row['baseline_json_total_bytes'] = baseline['mean_total_bytes']
                    trend_rows.append(row)
    finally:
        if gc_enabled:
            gc.enable()

    measurements.sort(key=_measurement_sort_key)
    trend_measurements = _build_trend_measurements(measurements, trend_rows)
    trend_regressions = _build_trend_regressions(trend_measurements)
    return {
        'cycles': cycles,
        'steady_state_warmup': steady_state_warmup,
        'trend_cycles': trend_cycles,
        'trend_row_counts': trend_row_counts,
        'measurements': measurements,
        'trend_measurements': trend_measurements,
        'trend_regressions': trend_regressions,
        'timing_tradeoffs': _build_timing_tradeoffs(measurements),
        'recommendations': _build_recommendations(measurements),
    }


def render_report(report: dict[str, object]) -> str:
    measurements = report['measurements']
    trend_measurements = report['trend_measurements']
    timing_tradeoffs = report['timing_tradeoffs']
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

    trend_rows = [{
        'series': row['series_title'],
        'list_size': row['list_size'],
        'reduction_pct': row['payload_reduction_pct'],
        'wire': row['steady_state_wire_mode'],
        'total_b': row['mean_total_bytes'],
    } for row in trend_measurements]

    tradeoff_rows = [{
        'scenario': row['scenario'],
        'size': row['size'],
        'technique': row['technique'],
        'payload_pct': row['payload_reduction_pct'],
        'ser_pct': row['serialize_change_pct'],
        'ser_note': row['serialize_note'],
        'deser_pct': row['deserialize_change_pct'],
        'deser_note': row['deserialize_note'],
    } for row in timing_tradeoffs]

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
        '## Packed-binary trend graph',
        'Scatter points show measured payload reduction vs the same-family JSON baseline; lines are quadratic regression curves over those points.',
        _render_payload_reduction_svg(trend_measurements, report['trend_regressions']),
        '',
        '## Packed-binary trend data',
        _render_table(trend_rows, [
            ('series', 'series'),
            ('list_size', 'list size'),
            ('reduction_pct', 'payload reduction %'),
            ('wire', 'wire'),
            ('total_b', 'total bytes'),
        ]),
        '',
        '## Timing tradeoffs vs plain JSON',
        _render_table(tradeoff_rows, [
            ('scenario', 'scenario'),
            ('size', 'size'),
            ('technique', 'technique'),
            ('payload_pct', 'payload reduction %'),
            ('ser_pct', 'serialize Δ%'),
            ('ser_note', 'serialize'),
            ('deser_pct', 'deserialize Δ%'),
            ('deser_note', 'deserialize'),
        ]),
        '',
        '## Recommendations',
        *[f'- {recommendation}' for recommendation in report['recommendations']],
    ])


def run_benchmark_sync(
    cycles: int = 80,
    steady_state_warmup: int = 4,
    trend_cycles: int | None = None,
    trend_row_counts: list[int] | None = None,
) -> dict[str, object]:
    return asyncio.run(
        run_benchmark(
            cycles=cycles,
            steady_state_warmup=steady_state_warmup,
            trend_cycles=trend_cycles,
            trend_row_counts=trend_row_counts,
        )
    )


def _parse_row_counts(value: str) -> list[int]:
    return [int(part.strip()) for part in value.split(',') if part.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Run the Telepact Python performance harness.')
    parser.add_argument('--cycles', type=int, default=80, help='Steady-state samples to collect per permutation.')
    parser.add_argument('--steady-state-warmup', type=int, default=4, help='Extra steady-state warmup samples to discard after negotiation.')
    parser.add_argument('--trend-cycles', type=int, help='Steady-state samples to collect per list-size trend point.')
    parser.add_argument(
        '--trend-row-counts',
        type=_parse_row_counts,
        help='Comma-separated row counts to use for list-size trend plotting (for example: 8,16,32,64,128).',
    )
    args = parser.parse_args(argv)

    report = run_benchmark_sync(
        cycles=args.cycles,
        steady_state_warmup=args.steady_state_warmup,
        trend_cycles=args.trend_cycles,
        trend_row_counts=args.trend_row_counts,
    )
    print(render_report(report))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
