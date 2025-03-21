//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

import { MockInvocation } from '../../internal/mock/MockInvocation';

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
