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

from harness import run_harness


def test_performance_example_reports_steady_state_metrics() -> None:
    results, report = run_harness()
    print(report)

    assert 'steady-state' in report
    assert 'binary and packed rows exclude the initial negotiation request' in report
    assert results['small-json'].warmup_requests == 0
    assert results['small-binary'].warmup_requests == 1
    assert results['small-packed'].warmup_requests == 1
    assert results['big-binary'].warmup_requests == 1
    assert results['big-packed'].warmup_requests == 1
    assert results['big-packed-unsafe'].warmup_requests == 1
    assert results['big-packed-select'].warmup_requests == 1

    assert results['small-json'].response_item_count == 3
    assert results['big-json'].response_item_count == 250

    assert results['small-binary'].total_size_bytes < results['small-json'].total_size_bytes
    assert results['small-packed'].total_size_bytes <= results['small-binary'].total_size_bytes
    assert results['big-binary'].total_size_bytes < results['big-json'].total_size_bytes
    assert results['big-packed'].total_size_bytes < results['big-binary'].total_size_bytes
    assert results['big-packed-select'].total_size_bytes < results['big-packed'].total_size_bytes

    assert '@enc_' not in results['small-binary'].observed_response_headers
    assert '@enc_' not in results['small-packed'].observed_response_headers
    assert '@enc_' not in results['big-binary'].observed_response_headers
    assert '@enc_' not in results['big-packed'].observed_response_headers
    assert '@enc_' not in results['big-packed-unsafe'].observed_response_headers
    assert '@enc_' not in results['big-packed-select'].observed_response_headers
