import { MockInvocation } from 'uapi/internal/mock/MockInvocation';

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
