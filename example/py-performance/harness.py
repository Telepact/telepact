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
from dataclasses import dataclass
from statistics import median
from time import perf_counter_ns

from telepact import Client, Message, Serializer

from server import build_telepact_server


ITERATIONS = 60
BINARY_HANDSHAKE_REQUESTS = 1

SELECT_HEADERS = {
    '@select_': {
        '->': {
            'Ok_': ['summary', 'items'],
        },
        'struct.PerformanceSummary': ['profile', 'itemCount'],
        'struct.PerformanceItem': ['id', 'sku', 'priceCents', 'available'],
    }
}


@dataclass(frozen=True)
class Scenario:
    name: str
    profile: str
    use_binary: bool
    always_send_json: bool
    headers: dict[str, object]


@dataclass(frozen=True)
class Observation:
    request_size: int
    response_size: int
    serialize_ns: int
    deserialize_ns: int
    round_trip_ns: int
    request_is_json: bool
    response_headers: dict[str, object]
    response_body: dict[str, object]


@dataclass(frozen=True)
class ScenarioMetrics:
    scenario: Scenario
    iterations: int
    warmup_requests: int
    request_size_bytes: int
    response_size_bytes: int
    total_size_bytes: int
    serialize_us: float
    deserialize_us: float
    round_trip_us: float
    observed_response_headers: tuple[str, ...]
    response_item_count: int


@dataclass(frozen=True)
class NetworkProfile:
    name: str
    bandwidth_mbps: float
    distance_km: float
    overhead_ms: float


class MeasuringAdapter:
    def __init__(self) -> None:
        self.server = build_telepact_server()
        self.observations: list[Observation] = []

    async def __call__(self, message: Message, serializer: Serializer) -> Message:
        serialize_start = perf_counter_ns()
        request_bytes = serializer.serialize(message)
        serialize_end = perf_counter_ns()

        round_trip_start = perf_counter_ns()
        response = await self.server.process(request_bytes)
        deserialize_start = perf_counter_ns()
        message_response = serializer.deserialize(response.bytes)
        round_trip_end = perf_counter_ns()

        self.observations.append(Observation(
            request_size=len(request_bytes),
            response_size=len(response.bytes),
            serialize_ns=serialize_end - serialize_start,
            deserialize_ns=round_trip_end - deserialize_start,
            round_trip_ns=round_trip_end - round_trip_start,
            request_is_json=request_bytes[:1] == b'[',
            response_headers={str(key): value for key, value in message_response.headers.items()},
            response_body={str(key): value for key, value in message_response.body.items()},
        ))
        return message_response


def _median_int(values: list[int]) -> int:
    return int(round(median(values)))


def _median_us(values: list[int]) -> float:
    return median(values) / 1_000.0


def _request_message(scenario: Scenario) -> Message:
    headers = dict(scenario.headers)
    return Message(headers, {'fn.getCatalog': {'profile': scenario.profile}})


async def _run_scenario(scenario: Scenario) -> ScenarioMetrics:
    adapter = MeasuringAdapter()
    options = Client.Options()
    options.use_binary = scenario.use_binary
    options.always_send_json = scenario.always_send_json
    client = Client(adapter, options)

    warmup_requests = BINARY_HANDSHAKE_REQUESTS if scenario.use_binary else 0
    request_message = _request_message(scenario)

    for _ in range(warmup_requests):
        await client.request(request_message)

    warmup_observations = list(adapter.observations)

    for _ in range(ITERATIONS):
        await client.request(request_message)

    steady_state_observations = adapter.observations[warmup_requests:]

    if scenario.use_binary:
        assert len(warmup_observations) == BINARY_HANDSHAKE_REQUESTS
        assert '@enc_' in warmup_observations[0].response_headers
        assert all('@enc_' not in observation.response_headers for observation in steady_state_observations)
        assert all(not observation.request_is_json for observation in steady_state_observations)

    response_headers = tuple(sorted({
        header
        for observation in steady_state_observations
        for header in observation.response_headers
    }))
    response_payload = steady_state_observations[0].response_body['Ok_']

    return ScenarioMetrics(
        scenario=scenario,
        iterations=ITERATIONS,
        warmup_requests=warmup_requests,
        request_size_bytes=_median_int([observation.request_size for observation in steady_state_observations]),
        response_size_bytes=_median_int([observation.response_size for observation in steady_state_observations]),
        total_size_bytes=_median_int([
            observation.request_size + observation.response_size
            for observation in steady_state_observations
        ]),
        serialize_us=_median_us([observation.serialize_ns for observation in steady_state_observations]),
        deserialize_us=_median_us([observation.deserialize_ns for observation in steady_state_observations]),
        round_trip_us=_median_us([observation.round_trip_ns for observation in steady_state_observations]),
        observed_response_headers=response_headers,
        response_item_count=len(response_payload['items']),
    )


def _scenario_rows(results: dict[str, ScenarioMetrics]) -> list[str]:
    header = (
        'scenario'.ljust(20)
        + 'items'.rjust(7)
        + ' warmup'.rjust(8)
        + ' req'.rjust(8)
        + ' resp'.rjust(8)
        + ' total'.rjust(9)
        + ' ser-us'.rjust(10)
        + ' de-us'.rjust(10)
        + ' rt-us'.rjust(10)
    )
    rows = [header, '-' * len(header)]
    for name in (
        'small-json',
        'small-binary',
        'small-packed',
        'big-json',
        'big-binary',
        'big-packed',
        'big-packed-unsafe',
        'big-packed-select',
    ):
        metric = results[name]
        rows.append(
            name.ljust(20)
            + str(metric.response_item_count).rjust(7)
            + str(metric.warmup_requests).rjust(8)
            + str(metric.request_size_bytes).rjust(8)
            + str(metric.response_size_bytes).rjust(8)
            + str(metric.total_size_bytes).rjust(9)
            + f'{metric.serialize_us:10.1f}'
            + f'{metric.deserialize_us:10.1f}'
            + f'{metric.round_trip_us:10.1f}'
        )
    return rows


def _estimate_latency_ms(profile: NetworkProfile, total_size_bytes: int) -> float:
    transfer_ms = (total_size_bytes * 8.0) / (profile.bandwidth_mbps * 1_000_000.0) * 1_000.0
    propagation_ms = profile.distance_km / 100.0
    return profile.overhead_ms + propagation_ms + transfer_ms


def _latency_rows(title: str, baseline_name: str, scenario_names: tuple[str, ...], results: dict[str, ScenarioMetrics]) -> list[str]:
    profiles = (
        NetworkProfile('LAN / 20km', 1_000.0, 20.0, 0.3),
        NetworkProfile('Metro fiber / 250km', 200.0, 250.0, 1.5),
        NetworkProfile('Regional WAN / 1200km', 100.0, 1_200.0, 6.0),
        NetworkProfile('Cross-country / 4000km', 50.0, 4_000.0, 14.0),
        NetworkProfile('Intercontinental / 9000km', 20.0, 9_000.0, 28.0),
        NetworkProfile('4G mobile / 1500km', 10.0, 1_500.0, 45.0),
    )
    rows = [title]
    header = 'profile'.ljust(29)
    for scenario_name in scenario_names:
        header += scenario_name.rjust(20)
    rows.append(header)
    rows.append('-' * len(header))

    for profile in profiles:
        row = profile.name.ljust(29)
        baseline_ms = _estimate_latency_ms(profile, results[baseline_name].total_size_bytes)
        for scenario_name in scenario_names:
            estimated_ms = _estimate_latency_ms(profile, results[scenario_name].total_size_bytes)
            saved_ms = baseline_ms - estimated_ms
            row += f'{estimated_ms:8.2f}ms ({saved_ms:+6.2f})'.rjust(20)
        rows.append(row)
    return rows


def _summary_rows(results: dict[str, ScenarioMetrics]) -> list[str]:
    big_json = results['big-json']
    big_binary = results['big-binary']
    big_packed = results['big-packed']
    big_packed_unsafe = results['big-packed-unsafe']
    big_packed_select = results['big-packed-select']

    return [
        'Key takeaways',
        f'- big binary removes {big_json.total_size_bytes - big_binary.total_size_bytes} steady-state bytes versus big JSON',
        f'- big packed removes {big_binary.total_size_bytes - big_packed.total_size_bytes} additional steady-state bytes versus big binary',
        f'- big packed + @select_ removes {big_packed.total_size_bytes - big_packed_select.total_size_bytes} steady-state bytes versus big packed',
        f'- big packed + @unsafe_ changed median round-trip time by {big_packed.round_trip_us - big_packed_unsafe.round_trip_us:.1f}us versus big packed',
    ]


def render_report(results: dict[str, ScenarioMetrics]) -> str:
    sections = [
        'Telepact Python performance harness (steady-state)',
        f'- iterations per scenario: {ITERATIONS}',
        '- binary and packed rows exclude the initial negotiation request from the reported metrics',
        '',
        * _scenario_rows(results),
        '',
        *_summary_rows(results),
        '',
        'Estimated request+response latency from steady-state serialized sizes',
        '',
        *_latency_rows(
            'Small payloads: ms (savings vs small-json)',
            'small-json',
            ('small-json', 'small-binary', 'small-packed'),
            results,
        ),
        '',
        *_latency_rows(
            'Big payloads: ms (savings vs big-json)',
            'big-json',
            ('big-json', 'big-binary', 'big-packed', 'big-packed-select'),
            results,
        ),
    ]
    return '\n'.join(sections)


async def collect_metrics() -> dict[str, ScenarioMetrics]:
    scenarios = (
        Scenario('small-json', 'small', False, True, {}),
        Scenario('small-binary', 'small', True, False, {}),
        Scenario('small-packed', 'small', True, False, {'@pac_': True}),
        Scenario('big-json', 'big', False, True, {}),
        Scenario('big-binary', 'big', True, False, {}),
        Scenario('big-packed', 'big', True, False, {'@pac_': True}),
        Scenario('big-packed-unsafe', 'big', True, False, {'@pac_': True, '@unsafe_': True}),
        Scenario('big-packed-select', 'big', True, False, {'@pac_': True, **SELECT_HEADERS}),
    )
    results: dict[str, ScenarioMetrics] = {}
    for scenario in scenarios:
        results[scenario.name] = await _run_scenario(scenario)
    return results


def run_harness() -> tuple[dict[str, ScenarioMetrics], str]:
    results = asyncio.run(collect_metrics())
    return results, render_report(results)
