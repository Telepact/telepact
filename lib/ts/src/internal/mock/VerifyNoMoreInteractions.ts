//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { MockInvocation } from '../../internal/mock/MockInvocation.js';

export function verifyNoMoreInteractions(invocations: MockInvocation[]): {
    [key: string]: any;
} {
    const invocationsNotVerified = invocations.filter((i) => !i.verified);

    if (invocationsNotVerified.length > 0) {
        const unverifiedCallsPseudoJson = invocationsNotVerified.map((invocation) => ({
            [invocation.functionName]: invocation.functionArgument,
        }));

        return {
            ErrorVerificationFailure: {
                additionalUnverifiedCalls: unverifiedCallsPseudoJson,
            },
        };
    }

    return { Ok_: {} };
}
