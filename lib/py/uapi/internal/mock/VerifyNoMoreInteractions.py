from typing import List, Dict, Any

from uapi.internal.mock.MockInvocation import MockInvocation


def verify_no_more_interactions(invocations: List['MockInvocation']) -> Dict[str, Any]:
    invocations_not_verified = [i for i in invocations if not i.verified]

    if invocations_not_verified:
        unverified_calls_pseudo_json = []
        for invocation in invocations_not_verified:
            unverified_calls_pseudo_json.append(
                {invocation.function_name: invocation.function_argument})
        return {
            "ErrorVerificationFailure": {
                "additionalUnverifiedCalls": unverified_calls_pseudo_json
            }
        }

    return {"Ok_": {}}
