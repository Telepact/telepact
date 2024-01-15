package io.github.brenbar.uapi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.TreeMap;

class _MockVerifyUtil {

    static Map<String, Object> verify(String functionName, Map<String, Object> argument,
            boolean exactMatch,
            Map<String, Object> verificationTimes, List<Invocation> invocations) {
        var matchesFound = 0;
        for (final var invocation : invocations) {
            if (Objects.equals(invocation.functionName, functionName)) {
                if (exactMatch) {
                    if (Objects.equals(invocation.functionArgument, argument)) {
                        invocation.verified = true;
                        matchesFound += 1;
                    }
                } else {
                    boolean isSubMap = _MockServerUtil.isSubMap(argument, invocation.functionArgument);
                    if (isSubMap) {
                        invocation.verified = true;
                        matchesFound += 1;
                    }
                }
            }
        }

        final var allCallsPseudoJson = new ArrayList<Map<String, Object>>();
        for (final var invocation : invocations) {
            allCallsPseudoJson.add(Map.of(invocation.functionName, invocation.functionArgument));
        }

        final Map.Entry<String, Object> verifyTimesEntry = _UUnion.entry(verificationTimes);
        final var verifyKey = verifyTimesEntry.getKey();
        final var verifyTimesStruct = (Map<String, Object>) verifyTimesEntry.getValue();

        Map<String, Object> verificationFailurePseudoJson = null;
        if (verifyKey.equals("Exact")) {
            final var times = (Integer) verifyTimesStruct.get("times");
            if (matchesFound > times) {
                verificationFailurePseudoJson = Map.of("TooManyMatchingCalls",
                        new TreeMap<>(Map.ofEntries(
                                Map.entry("wanted", Map.of("Exact", Map.of("times", times))),
                                Map.entry("found", matchesFound),
                                Map.entry("allCalls", allCallsPseudoJson))));
            } else if (matchesFound < times) {
                verificationFailurePseudoJson = Map.of("TooFewMatchingCalls",
                        new TreeMap<>(Map.ofEntries(
                                Map.entry("wanted", Map.of("Exact", Map.of("times", times))),
                                Map.entry("found", matchesFound),
                                Map.entry("allCalls", allCallsPseudoJson))));
            }
        } else if (verifyKey.equals("AtMost")) {
            final var times = (Integer) verifyTimesStruct.get("times");
            if (matchesFound > times) {
                verificationFailurePseudoJson = Map.of("TooManyMatchingCalls",
                        new TreeMap<>(Map.ofEntries(
                                Map.entry("wanted", Map.of("AtMost", Map.of("times", times))),
                                Map.entry("found", matchesFound),
                                Map.entry("allCalls", allCallsPseudoJson))));
            }
        } else if (verifyKey.equals("AtLeast")) {
            final var times = (Integer) verifyTimesStruct.get("times");
            if (matchesFound < times) {
                verificationFailurePseudoJson = Map.of("TooFewMatchingCalls",
                        new TreeMap<>(Map.ofEntries(
                                Map.entry("wanted", Map.of("AtLeast", Map.of("times", times))),
                                Map.entry("found", matchesFound),
                                Map.entry("allCalls", allCallsPseudoJson))));

            }
        }

        if (verificationFailurePseudoJson == null) {
            return Map.of("Ok", Map.of());
        }

        return Map.of("ErrorVerificationFailure", Map.of("reason", verificationFailurePseudoJson));
    }

    static Map<String, Object> verifyNoMoreInteractions(List<Invocation> invocations) {
        final var invocationsNotVerified = invocations.stream().filter(i -> !i.verified).toList();

        if (invocationsNotVerified.size() > 0) {
            final var unverifiedCallsPseudoJson = new ArrayList<Map<String, Object>>();
            for (final var invocation : invocationsNotVerified) {
                unverifiedCallsPseudoJson.add(Map.of(invocation.functionName, invocation.functionArgument));
            }
            return Map.of("ErrorVerificationFailure",
                    Map.of("additionalUnverifiedCalls", unverifiedCallsPseudoJson));
        }

        return Map.of("Ok", Map.of());
    }

}
