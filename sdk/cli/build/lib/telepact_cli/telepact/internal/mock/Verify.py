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

from typing import cast
from collections import OrderedDict
from ...internal.mock.IsSubMap import is_sub_map
from ...internal.mock.IsSubMapEntryEqual import is_sub_map_entry_equal
from ...internal.mock.MockInvocation import MockInvocation


def verify(function_name: str, argument: dict[str, object], exact_match: bool,
           verification_times: dict[str, object], invocations: list[MockInvocation]) -> dict[str, object]:
    matches_found = 0
    for invocation in invocations:
        if invocation.function_name == function_name:
            if exact_match:
                if invocation.function_argument == argument:
                    invocation.verified = True
                    matches_found += 1
            else:
                is_sub_map_result = is_sub_map(
                    argument, invocation.function_argument)
                if is_sub_map_result:
                    invocation.verified = True
                    matches_found += 1

    all_calls_pseudo_json = [OrderedDict(
        [(invocation.function_name, invocation.function_argument)]) for invocation in invocations]

    verify_times_entry = next(iter(verification_times.items()))
    verify_key = verify_times_entry[0]
    verify_times_struct = cast(dict[str, object], verify_times_entry[1])

    verification_failure_pseudo_json = None
    if verify_key == "Exact":
        times = cast(int, verify_times_struct["times"])
        if matches_found > times:
            verification_failure_pseudo_json = {"TooManyMatchingCalls": OrderedDict([
                ("wanted", {"Exact": {"times": times}}),
                ("found", matches_found),
                ("allCalls", all_calls_pseudo_json)
            ])}
        elif matches_found < times:
            verification_failure_pseudo_json = {"TooFewMatchingCalls": OrderedDict([
                ("wanted", {"Exact": {"times": times}}),
                ("found", matches_found),
                ("allCalls", all_calls_pseudo_json)
            ])}
    elif verify_key == "AtMost":
        times = cast(int, verify_times_struct["times"])
        if matches_found > times:
            verification_failure_pseudo_json = {"TooManyMatchingCalls": OrderedDict([
                ("wanted", {"AtMost": {"times": times}}),
                ("found", matches_found),
                ("allCalls", all_calls_pseudo_json)
            ])}
    elif verify_key == "AtLeast":
        times = cast(int, verify_times_struct["times"])
        if matches_found < times:
            verification_failure_pseudo_json = {"TooFewMatchingCalls": OrderedDict([
                ("wanted", {"AtLeast": {"times": times}}),
                ("found", matches_found),
                ("allCalls", all_calls_pseudo_json)
            ])}

    if verification_failure_pseudo_json is None:
        return {"Ok_": {}}

    return {"ErrorVerificationFailure": {"reason": verification_failure_pseudo_json}}
