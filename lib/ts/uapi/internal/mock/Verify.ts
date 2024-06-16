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
                if (isSubMapEntryEqual(invocation.functionArgument, argument)) {
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
