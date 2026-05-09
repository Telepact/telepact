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
    trend_measurements = report['trend_measurements']
    timing_tradeoffs = report['timing_tradeoffs']

    assert len(measurements) == 120
    assert all(row['steady_state_samples'] == 6 for row in measurements)
    assert any(row['use_packed'] and row['steady_state_wire_mode'] == 'packed-binary' for row in measurements)
    assert all(not row['steady_state_handshake_seen'] for row in measurements)
    assert len(trend_measurements) == 48
    assert report['trend_regressions']
    assert timing_tradeoffs

    binary_rows = [row for row in measurements if row['client_mode'] == 'binary']
    assert binary_rows
    assert all(row['discarded_handshake_samples'] >= 1 for row in binary_rows)

    dashboard_full = next(
        row for row in measurements
        if row['scenario'] == 'dashboard'
        and row['size'] == 'big'
        and row['client_mode'] == 'json'
        and not row['use_packed']
        and not row['use_select']
        and not row['use_unsafe']
    )
    dashboard_selected = next(
        row for row in measurements
        if row['scenario'] == 'dashboard'
        and row['size'] == 'big'
        and row['client_mode'] == 'json'
        and not row['use_packed']
        and row['use_select']
        and not row['use_unsafe']
    )
    assert dashboard_selected['mean_total_bytes'] < dashboard_full['mean_total_bytes']

    integer_json = next(
        row for row in measurements
        if row['scenario'] == 'integer_row_batch'
        and row['size'] == 'big'
        and row['client_mode'] == 'json'
        and not row['use_packed']
        and not row['use_select']
        and not row['use_unsafe']
    )
    integer_packed = next(
        row for row in measurements
        if row['scenario'] == 'integer_row_batch'
        and row['size'] == 'big'
        and row['client_mode'] == 'binary'
        and row['use_packed']
        and not row['use_select']
        and not row['use_unsafe']
    )
    assert integer_packed['mean_total_bytes'] < integer_json['mean_total_bytes']

    integer_trend_packed = [
        row for row in trend_measurements
        if row['series_key'] == 'integers_packed_binary'
    ]
    typical_trend_packed = [
        row for row in trend_measurements
        if row['series_key'] == 'typical_packed_binary'
    ]
    assert integer_trend_packed
    assert typical_trend_packed
    assert max(row['payload_reduction_pct'] for row in integer_trend_packed) > max(
        row['payload_reduction_pct'] for row in typical_trend_packed
    )

    packed_tradeoff = next(
        row for row in timing_tradeoffs
        if row['scenario'] == 'integer_row_batch'
        and row['size'] == 'big'
        and row['technique'] == '@pac_ (binary)'
    )
    assert packed_tradeoff['payload_reduction_pct'] > 0

    rendered = render_report(report)
    assert 'Steady-state metrics only.' in rendered
    assert '## Measurements' in rendered
    assert '## Packed-binary trend graph' in rendered
    assert '<svg' in rendered
    assert '## Timing tradeoffs vs plain JSON' in rendered
    assert '## Recommendations' in rendered
