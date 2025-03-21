package io.github.telepact.internal.mock;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class VerifyNoMoreInteractions {
    static Map<String, Object> verifyNoMoreInteractions(List<MockInvocation> invocations) {
        final var invocationsNotVerified = invocations.stream().filter(i -> !i.verified).toList();

        if (invocationsNotVerified.size() > 0) {
            final var unverifiedCallsPseudoJson = new ArrayList<Map<String, Object>>();
            for (final var invocation : invocationsNotVerified) {
                unverifiedCallsPseudoJson.add(Map.of(invocation.functionName, invocation.functionArgument));
            }
            return Map.of("ErrorVerificationFailure",
                    Map.of("additionalUnverifiedCalls", unverifiedCallsPseudoJson));
        }

        return Map.of("Ok_", Map.of());
    }
}
