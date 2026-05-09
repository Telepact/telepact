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

from harness import render_report, run_benchmark_sync


def test_performance_harness_reports_steady_state_metrics() -> None:
    report = run_benchmark_sync(cycles=6, steady_state_warmup=2)
    measurements = report['measurements']

    assert len(measurements) == 32
    assert all(row['steady_state_samples'] == 6 for row in measurements)
    assert any(row['steady_state_wire_mode'] == 'packed-binary' for row in measurements)
    assert all(not row['steady_state_handshake_seen'] for row in measurements)

    binary_rows = [row for row in measurements if row['client_mode'] == 'binary']
    assert binary_rows
    assert all(row['discarded_handshake_samples'] >= 1 for row in binary_rows)

    dashboard_full = next(
        row for row in measurements
        if row['scenario'] == 'dashboard'
        and row['size'] == 'big'
        and row['client_mode'] == 'json'
        and not row['use_select']
        and not row['use_unsafe']
    )
    dashboard_selected = next(
        row for row in measurements
        if row['scenario'] == 'dashboard'
        and row['size'] == 'big'
        and row['client_mode'] == 'json'
        and row['use_select']
        and not row['use_unsafe']
    )
    assert dashboard_selected['mean_total_bytes'] < dashboard_full['mean_total_bytes']

    rendered = render_report(report)
    assert 'Steady-state metrics only.' in rendered
    assert '## Measurements' in rendered
    assert '## Recommendations' in rendered
