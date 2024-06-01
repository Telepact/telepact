from typing import Any, Dict, List, Union
from collections import OrderedDict

from uapi.internal.mock.IsSubMap import is_sub_map


def verify(function_name: str, argument: Dict[str, Any], exact_match: bool,
           verification_times: Dict[str, Any], invocations: List[Dict[str, Any]]) -> Dict[str, Any]:
    matches_found = 0
    for invocation in invocations:
        if invocation['functionName'] == function_name:
            if exact_match:
                if invocation['functionArgument'] == argument:
                    invocation['verified'] = True
                    matches_found += 1
            else:
                is_sub_map_result = is_sub_map(
                    argument, invocation['functionArgument'])
                if is_sub_map_result:
                    invocation['verified'] = True
                    matches_found += 1

    all_calls_pseudo_json = []
    for invocation in invocations:
        all_calls_pseudo_json.append(
            {invocation['functionName']: invocation['functionArgument']})

    verify_times_entry = next(iter(verification_times.items()))
    verify_key = verify_times_entry[0]
    verify_times_struct = verify_times_entry[1]

    verification_failure_pseudo_json = None
    if verify_key == "Exact":
        times = verify_times_struct['times']
        if matches_found > times:
            verification_failure_pseudo_json = {
                "TooManyMatchingCalls": OrderedDict([
                    ("wanted", {"Exact": {"times": times}}),
                    ("found", matches_found),
                    ("allCalls", all_calls_pseudo_json)
                ])
            }
        elif matches_found < times:
            verification_failure_pseudo_json = {
                "TooFewMatchingCalls": OrderedDict([
                    ("wanted", {"Exact": {"times": times}}),
                    ("found", matches_found),
                    ("allCalls", all_calls_pseudo_json)
                ])
            }
    elif verify_key == "AtMost":
        times = verify_times_struct['times']
        if matches_found > times:
            verification_failure_pseudo_json = {
                "TooManyMatchingCalls": OrderedDict([
                    ("wanted", {"AtMost": {"times": times}}),
                    ("found", matches_found),
                    ("allCalls", all_calls_pseudo_json)
                ])
            }
    elif verify_key == "AtLeast":
        times = verify_times_struct['times']
        if matches_found < times:
            verification_failure_pseudo_json = {
                "TooFewMatchingCalls": OrderedDict([
                    ("wanted", {"AtLeast": {"times": times}}),
                    ("found", matches_found),
                    ("allCalls", all_calls_pseudo_json)
                ])
            }

    if verification_failure_pseudo_json is None:
        return {"Ok_": {}}

    return {"ErrorVerificationFailure": {"reason": verification_failure_pseudo_json}}
