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

import { objectsAreEqual } from '../ObjectsAreEqual';
import { isSubMap } from './IsSubMap';
import { isSubMapEntryEqual } from './IsSubMapEntryEqual';
import { MockInvocation } from './MockInvocation';

export function verify(
    functionName: string,
    argument: { [key: string]: any },
    exactMatch: boolean,
    verificationTimes: { [key: string]: any },
    invocations: MockInvocation[],
): { [key: string]: any } {
    let matchesFound = 0;
    for (const invocation of invocations) {
        if (invocation.functionName === functionName) {
            if (exactMatch) {
                if (objectsAreEqual(invocation.functionArgument, argument)) {
                    invocation.verified = true;
                    matchesFound += 1;
                }
            } else {
                const isSubMapResult = isSubMap(argument, invocation.functionArgument);
                if (isSubMapResult) {
                    invocation.verified = true;
                    matchesFound += 1;
                }
            }
        }
    }

    const allCallsPseudoJson = invocations.map((invocation) => ({
        [invocation.functionName]: invocation.functionArgument,
    }));

    const verifyTimesEntry = Object.entries(verificationTimes)[0];
    const verifyKey = verifyTimesEntry[0];
    const verifyTimesStruct = verifyTimesEntry[1] as { [key: string]: any };

    let verificationFailurePseudoJson: { [key: string]: any } | null = null;
    if (verifyKey === 'Exact') {
        const times = verifyTimesStruct.times as number;
        if (matchesFound > times) {
            verificationFailurePseudoJson = {
                TooManyMatchingCalls: {
                    wanted: { Exact: { times } },
                    found: matchesFound,
                    allCalls: allCallsPseudoJson,
                },
            };
        } else if (matchesFound < times) {
            verificationFailurePseudoJson = {
                TooFewMatchingCalls: {
                    wanted: { Exact: { times } },
                    found: matchesFound,
                    allCalls: allCallsPseudoJson,
                },
            };
        }
    } else if (verifyKey === 'AtMost') {
        const times = verifyTimesStruct.times as number;
        if (matchesFound > times) {
            verificationFailurePseudoJson = {
                TooManyMatchingCalls: {
                    wanted: { AtMost: { times } },
                    found: matchesFound,
                    allCalls: allCallsPseudoJson,
                },
            };
        }
    } else if (verifyKey === 'AtLeast') {
        const times = verifyTimesStruct.times as number;
        if (matchesFound < times) {
            verificationFailurePseudoJson = {
                TooFewMatchingCalls: {
                    wanted: { AtLeast: { times } },
                    found: matchesFound,
                    allCalls: allCallsPseudoJson,
                },
            };
        }
    }

    if (verificationFailurePseudoJson === null) {
        return { Ok_: {} };
    }

    return { ErrorVerificationFailure: { reason: verificationFailurePseudoJson } };
}
