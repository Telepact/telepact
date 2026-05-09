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

from benchmark import MODES, PROFILES, SIZES, Scenario, format_report, run_harness


def test_performance_harness_reports_all_steady_state_permutations() -> None:
    results = run_harness()
    print(format_report(results))

    assert len(results) == len(PROFILES) * len(SIZES) * len(MODES) * 2 * 2

    by_scenario = {result.scenario: result for result in results}

    for result in results:
        scenario = result.scenario
        assert result.steady_state_request_bytes > 0
        assert result.steady_state_response_bytes > 0
        assert result.serialize.median_us > 0
        assert result.deserialize.median_us > 0
        assert result.roundtrip.median_us > 0
        assert set(result.estimated_network_savings_ms.keys()) == {
            'wifi-lan',
            '5g-metro',
            'regional-fiber',
            'intercontinental',
        }

        if scenario.mode == 'json':
            assert result.steady_state_request_wire_format == 'json'
            assert result.steady_state_response_wire_format == 'json'
        else:
            assert result.warmup_request_wire_format == 'json'
            assert result.steady_state_request_wire_format == 'msgpack'
            assert result.steady_state_response_wire_format == 'msgpack'
            assert result.warmup_request_bytes != result.steady_state_request_bytes

        selected = by_scenario[Scenario(scenario.profile, scenario.size, scenario.mode, scenario.unsafe, True)]
        full = by_scenario[Scenario(scenario.profile, scenario.size, scenario.mode, scenario.unsafe, False)]
        if scenario.select:
            assert selected.steady_state_total_bytes < full.steady_state_total_bytes

    big_binary = by_scenario[Scenario('numbers', 'big', 'binary', False, False)]
    big_json = by_scenario[Scenario('numbers', 'big', 'json', False, False)]
    big_packed = by_scenario[Scenario('numbers', 'big', 'packed-binary', False, False)]
    assert big_binary.steady_state_total_bytes < big_json.steady_state_total_bytes
    assert big_packed.steady_state_total_bytes <= big_binary.steady_state_total_bytes
