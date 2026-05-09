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

import asyncio
import copy
import statistics
import time
from dataclasses import dataclass
from typing import Literal

from telepact import Client, Message, Serializer

from server import build_telepact_server

DEFAULT_TIMEOUT_MS = 5000
ROUNDTRIP_CYCLES = 31
SERIALIZATION_CYCLES = 120
PROFILES = ('typical', 'strings', 'numbers')
SIZES = ('small', 'big')
MODES = ('json', 'binary', 'packed-binary')

Mode = Literal['json', 'binary', 'packed-binary']
Profile = Literal['typical', 'strings', 'numbers']
Size = Literal['small', 'big']


@dataclass(frozen=True)
class Scenario:
    profile: Profile
    size: Size
    mode: Mode
    unsafe: bool
    select: bool


@dataclass(frozen=True)
class Exchange:
    request_size: int
    response_size: int
    request_wire_format: str
    response_wire_format: str


@dataclass(frozen=True)
class Stats:
    median_us: float
    mean_us: float
    p95_us: float
    stdev_us: float


@dataclass(frozen=True)
class NetworkProfile:
    key: str
    label: str
    bandwidth_mbps: float
    rtt_ms: float
    distance_km: int


@dataclass(frozen=True)
class ScenarioMetrics:
    scenario: Scenario
    steady_state_request_bytes: int
    steady_state_response_bytes: int
    steady_state_total_bytes: int
    warmup_request_bytes: int
    warmup_response_bytes: int
    warmup_request_wire_format: str
    warmup_response_wire_format: str
    steady_state_request_wire_format: str
    steady_state_response_wire_format: str
    serialize: Stats
    deserialize: Stats
    roundtrip: Stats
    estimated_network_savings_ms: dict[str, float]


NETWORK_PROFILES = (
    NetworkProfile('wifi-lan', 'Wi-Fi / LAN', bandwidth_mbps=100.0, rtt_ms=2.0, distance_km=1),
    NetworkProfile('5g-metro', '5G metro', bandwidth_mbps=35.0, rtt_ms=18.0, distance_km=25),
    NetworkProfile('regional-fiber', 'Regional fiber', bandwidth_mbps=20.0, rtt_ms=32.0, distance_km=800),
    NetworkProfile('intercontinental', 'Intercontinental WAN', bandwidth_mbps=8.0, rtt_ms=120.0, distance_km=8000),
)


def _detect_wire_format(payload: bytes) -> str:
    return 'msgpack' if payload and payload[0] == 0x92 else 'json'


class _InProcessTransport:
    def __init__(self):
        self.server = build_telepact_server()
        self.exchanges: list[Exchange] = []
        self.last_request_bytes = b''
        self.last_response_bytes = b''

    async def adapter(self, message: Message, serializer: Serializer) -> Message:
        request_bytes = serializer.serialize(message)
        response = await self.server.process(request_bytes)
        self.last_request_bytes = request_bytes
        self.last_response_bytes = response.bytes
        self.exchanges.append(
            Exchange(
                request_size=len(request_bytes),
                response_size=len(response.bytes),
                request_wire_format=_detect_wire_format(request_bytes),
                response_wire_format=_detect_wire_format(response.bytes),
            )
        )
        return serializer.deserialize(response.bytes)


def _select_header(profile: Profile) -> dict[str, object]:
    if profile == 'typical':
        return {
            '->': {'Ok_': ['profile', 'size', 'payload']},
            'union.Payload_': {'Typical': ['shipments']},
            'struct.TypicalShipment': ['shipmentId', 'address', 'items', 'riskScore'],
            'struct.Address': ['city', 'country'],
            'struct.TypicalItem': ['sku', 'quantity'],
        }
    if profile == 'strings':
        return {
            '->': {'Ok_': ['profile', 'size', 'payload']},
            'union.Payload_': {'StringHeavy': ['rows']},
            'struct.StringRow': ['id', 'title', 'slug'],
        }
    return {
        '->': {'Ok_': ['profile', 'size', 'payload']},
        'union.Payload_': {'NumberHeavy': ['rows', 'totals']},
        'struct.NumberRow': ['id', 'metricA', 'metricB'],
    }


def build_request_message(scenario: Scenario) -> Message:
    headers: dict[str, object] = {}
    if scenario.mode == 'packed-binary':
        headers['@pac_'] = True
    if scenario.unsafe:
        headers['@unsafe_'] = True
    if scenario.select:
        headers['@select_'] = _select_header(scenario.profile)
    return Message(headers, {
        'fn.getBenchmarkPayload': {
            'profile': scenario.profile,
            'size': scenario.size,
        },
    })


def build_transport_message(scenario: Scenario) -> Message:
    message = build_request_message(scenario)
    headers = copy.deepcopy(message.headers)
    headers['@time_'] = DEFAULT_TIMEOUT_MS
    if scenario.mode != 'json':
        headers['@binary_'] = True
    return Message(headers, copy.deepcopy(message.body))


def _stats_from_measurements(durations_ns: list[int]) -> Stats:
    durations_us = [duration / 1000 for duration in durations_ns]
    sorted_values = sorted(durations_us)
    p95_index = max(0, min(len(sorted_values) - 1, int((len(sorted_values) - 1) * 0.95)))
    stdev_us = statistics.pstdev(durations_us) if len(durations_us) > 1 else 0.0
    return Stats(
        median_us=statistics.median(sorted_values),
        mean_us=statistics.fmean(sorted_values),
        p95_us=sorted_values[p95_index],
        stdev_us=stdev_us,
    )


def _time_sync(operation, cycles: int) -> Stats:
    durations_ns = []
    for _ in range(cycles):
        started = time.perf_counter_ns()
        operation()
        durations_ns.append(time.perf_counter_ns() - started)
    return _stats_from_measurements(durations_ns)


async def _time_async(operation, cycles: int) -> Stats:
    durations_ns = []
    for _ in range(cycles):
        started = time.perf_counter_ns()
        await operation()
        durations_ns.append(time.perf_counter_ns() - started)
    return _stats_from_measurements(durations_ns)


def _estimated_total_ms(total_bytes: int, profile: NetworkProfile) -> float:
    transfer_ms = (total_bytes * 8 * 1000) / (profile.bandwidth_mbps * 1_000_000)
    return profile.rtt_ms + transfer_ms


async def _run_scenario(scenario: Scenario) -> ScenarioMetrics:
    transport = _InProcessTransport()
    options = Client.Options()
    options.use_binary = scenario.mode != 'json'
    options.always_send_json = False
    client = Client(transport.adapter, options)

    await client.request(build_request_message(scenario))
    warmup_exchange = transport.exchanges[-1]

    await client.request(build_request_message(scenario))
    steady_state_exchange = transport.exchanges[-1]
    steady_state_response_bytes = transport.last_response_bytes

    serialize_stats = _time_sync(
        lambda: client.serializer.serialize(build_transport_message(scenario)),
        SERIALIZATION_CYCLES,
    )
    deserialize_stats = _time_sync(
        lambda: client.serializer.deserialize(steady_state_response_bytes),
        SERIALIZATION_CYCLES,
    )
    roundtrip_stats = await _time_async(
        lambda: client.request(build_request_message(scenario)),
        ROUNDTRIP_CYCLES,
    )

    return ScenarioMetrics(
        scenario=scenario,
        steady_state_request_bytes=steady_state_exchange.request_size,
        steady_state_response_bytes=steady_state_exchange.response_size,
        steady_state_total_bytes=steady_state_exchange.request_size + steady_state_exchange.response_size,
        warmup_request_bytes=warmup_exchange.request_size,
        warmup_response_bytes=warmup_exchange.response_size,
        warmup_request_wire_format=warmup_exchange.request_wire_format,
        warmup_response_wire_format=warmup_exchange.response_wire_format,
        steady_state_request_wire_format=steady_state_exchange.request_wire_format,
        steady_state_response_wire_format=steady_state_exchange.response_wire_format,
        serialize=serialize_stats,
        deserialize=deserialize_stats,
        roundtrip=roundtrip_stats,
        estimated_network_savings_ms={},
    )


def _scenario_key(scenario: Scenario) -> tuple[str, str, bool, bool]:
    return (scenario.profile, scenario.size, scenario.unsafe, scenario.select)


def _describe_scenario(scenario: Scenario) -> str:
    return f'{scenario.size} {scenario.profile} | {scenario.mode} | unsafe={scenario.unsafe} | select={scenario.select}'


def _format_stats(stats: Stats) -> str:
    return f'{stats.median_us:.1f}/{stats.p95_us:.1f}'


def _format_network_savings(savings: dict[str, float]) -> str:
    ordered_keys = [profile.key for profile in NETWORK_PROFILES]
    return '/'.join(f'{savings[key]:.2f}' for key in ordered_keys)


def _render_table(headers: list[str], rows: list[list[str]]) -> str:
    widths = [len(header) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))
    divider = ' | '.join('-' * width for width in widths)
    lines = [
        ' | '.join(header.ljust(widths[index]) for index, header in enumerate(headers)),
        divider,
    ]
    for row in rows:
        lines.append(' | '.join(value.ljust(widths[index]) for index, value in enumerate(row)))
    return '\n'.join(lines)


def _build_recommendations(results: list[ScenarioMetrics]) -> list[str]:
    by_scenario = {result.scenario: result for result in results}

    select_candidates = []
    unsafe_candidates = []
    packed_candidates = []
    binary_candidates = []
    small_binary_candidates = []

    for result in results:
        scenario = result.scenario
        base_key = Scenario(scenario.profile, scenario.size, scenario.mode, scenario.unsafe, False)
        safe_key = Scenario(scenario.profile, scenario.size, scenario.mode, False, scenario.select)
        binary_key = Scenario(scenario.profile, scenario.size, 'binary', scenario.unsafe, scenario.select)
        json_key = Scenario(scenario.profile, scenario.size, 'json', scenario.unsafe, scenario.select)

        if scenario.select:
            base = by_scenario.get(base_key)
            if base is not None:
                saved = base.steady_state_total_bytes - result.steady_state_total_bytes
                select_candidates.append((saved, base, result))

        if scenario.unsafe:
            safe = by_scenario.get(safe_key)
            if safe is not None:
                saved = safe.roundtrip.median_us - result.roundtrip.median_us
                unsafe_candidates.append((saved, safe, result))

        if scenario.mode == 'packed-binary':
            binary = by_scenario.get(binary_key)
            if binary is not None:
                saved = binary.steady_state_total_bytes - result.steady_state_total_bytes
                packed_candidates.append((saved, binary, result))

        if scenario.mode == 'binary':
            json_result = by_scenario.get(json_key)
            if json_result is not None:
                saved = json_result.steady_state_total_bytes - result.steady_state_total_bytes
                binary_candidates.append((saved, json_result, result))
                if scenario.size == 'small':
                    small_binary_candidates.append((saved, json_result, result))

    recommendations = []

    if binary_candidates:
        saved, baseline, improved = max(binary_candidates, key=lambda item: item[0])
        pct = (saved / baseline.steady_state_total_bytes) * 100 if baseline.steady_state_total_bytes else 0.0
        recommendations.append(
            f'For long-lived connections, binary helps most on larger payloads: {_describe_scenario(improved.scenario)} saves {saved} bytes ({pct:.1f}%) per steady-state call versus JSON.'
        )

    if packed_candidates:
        saved, baseline, improved = max(packed_candidates, key=lambda item: item[0])
        pct = (saved / baseline.steady_state_total_bytes) * 100 if baseline.steady_state_total_bytes else 0.0
        recommendations.append(
            f'Use packed binary for repeated homogeneous records: {_describe_scenario(improved.scenario)} saves an extra {saved} bytes ({pct:.1f}%) over plain binary.'
        )

    if select_candidates:
        saved, baseline, improved = max(select_candidates, key=lambda item: item[0])
        pct = (saved / baseline.steady_state_total_bytes) * 100 if baseline.steady_state_total_bytes else 0.0
        recommendations.append(
            f'Use @select_ when clients do not need full results: {_describe_scenario(improved.scenario)} trims {saved} bytes ({pct:.1f}%) from the steady-state exchange.'
        )

    if unsafe_candidates:
        saved, baseline, improved = max(unsafe_candidates, key=lambda item: item[0])
        recommendations.append(
            f'Use @unsafe_ only for trusted paths with expensive responses: {_describe_scenario(improved.scenario)} reduces median in-process roundtrip time by {saved:.1f}µs.'
        )

    if small_binary_candidates:
        saved, baseline, improved = min(small_binary_candidates, key=lambda item: item[0])
        recommendations.append(
            f'Small payloads are less sensitive to wire format: {_describe_scenario(improved.scenario)} changes only {saved} bytes versus JSON, so transport simplicity may matter more there.'
        )

    return recommendations


def format_report(results: list[ScenarioMetrics]) -> str:
    recommendation_lines = [f'- {line}' for line in _build_recommendations(results)]
    network_rows = [
        [profile.key, profile.label, f'{profile.bandwidth_mbps:.1f}', f'{profile.rtt_ms:.1f}', str(profile.distance_km)]
        for profile in NETWORK_PROFILES
    ]
    scenario_rows = []
    for result in results:
        scenario = result.scenario
        scenario_rows.append([
            scenario.profile,
            scenario.size,
            scenario.mode,
            str(scenario.select),
            str(scenario.unsafe),
            str(result.steady_state_request_bytes),
            str(result.steady_state_response_bytes),
            str(result.steady_state_total_bytes),
            _format_stats(result.serialize),
            _format_stats(result.deserialize),
            _format_stats(result.roundtrip),
            f'{result.warmup_request_wire_format}->{result.steady_state_request_wire_format}',
            _format_network_savings(result.estimated_network_savings_ms),
        ])

    sections = [
        'Telepact steady-state performance harness',
        '',
        f'Permutations: {len(results)} ({len(PROFILES)} profiles × {len(SIZES)} sizes × {len(MODES)} modes × 2 unsafe settings × 2 select settings)',
        f'Cycles: {ROUNDTRIP_CYCLES} roundtrips, {SERIALIZATION_CYCLES} serialize ops, {SERIALIZATION_CYCLES} deserialize ops per permutation',
        'Steady-state note: binary and packed-binary rows exclude the initial negotiation exchange; the wire column shows warmup->steady-state request format.',
        '',
        'Recommendations',
        *recommendation_lines,
        '',
        'Network profiles (savings column order is wifi-lan/5g-metro/regional-fiber/intercontinental)',
        _render_table(
            ['key', 'label', 'bandwidthMbps', 'rttMs', 'distanceKm'],
            network_rows,
        ),
        '',
        'Scenario results (ser/deser/rt = median/p95 microseconds; netΔ = estimated steady-state savings vs JSON in ms)',
        _render_table(
            ['profile', 'size', 'mode', 'select', 'unsafe', 'reqB', 'respB', 'totalB', 'ser', 'deser', 'rt', 'wire', 'netΔ'],
            scenario_rows,
        ),
    ]
    return '\n'.join(sections)


async def _run_harness_async() -> list[ScenarioMetrics]:
    scenarios = [
        Scenario(profile, size, mode, unsafe, select)
        for profile in PROFILES
        for size in SIZES
        for mode in MODES
        for unsafe in (False, True)
        for select in (False, True)
    ]
    results = []
    for scenario in scenarios:
        results.append(await _run_scenario(scenario))

    by_scenario = {result.scenario: result for result in results}
    final_results = []
    for result in results:
        baseline = by_scenario[Scenario(result.scenario.profile, result.scenario.size, 'json', result.scenario.unsafe, result.scenario.select)]
        savings = {
            profile.key: round(
                _estimated_total_ms(baseline.steady_state_total_bytes, profile) - _estimated_total_ms(result.steady_state_total_bytes, profile),
                4,
            )
            for profile in NETWORK_PROFILES
        }
        final_results.append(
            ScenarioMetrics(
                scenario=result.scenario,
                steady_state_request_bytes=result.steady_state_request_bytes,
                steady_state_response_bytes=result.steady_state_response_bytes,
                steady_state_total_bytes=result.steady_state_total_bytes,
                warmup_request_bytes=result.warmup_request_bytes,
                warmup_response_bytes=result.warmup_response_bytes,
                warmup_request_wire_format=result.warmup_request_wire_format,
                warmup_response_wire_format=result.warmup_response_wire_format,
                steady_state_request_wire_format=result.steady_state_request_wire_format,
                steady_state_response_wire_format=result.steady_state_response_wire_format,
                serialize=result.serialize,
                deserialize=result.deserialize,
                roundtrip=result.roundtrip,
                estimated_network_savings_ms=savings,
            )
        )

    return sorted(
        final_results,
        key=lambda result: (
            PROFILES.index(result.scenario.profile),
            SIZES.index(result.scenario.size),
            MODES.index(result.scenario.mode),
            int(result.scenario.unsafe),
            int(result.scenario.select),
        ),
    )


def run_harness() -> list[ScenarioMetrics]:
    return asyncio.run(_run_harness_async())


if __name__ == '__main__':
    print(format_report(run_harness()))
