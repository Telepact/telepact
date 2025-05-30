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

package io.github.telepact.internal.mock;

import static io.github.telepact.internal.mock.IsSubMap.isSubMap;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.TreeMap;

public class Verify {
    static Map<String, Object> verify(String functionName, Map<String, Object> argument, boolean exactMatch,
            Map<String, Object> verificationTimes, List<MockInvocation> invocations) {
        var matchesFound = 0;
        for (final var invocation : invocations) {
            if (Objects.equals(invocation.functionName, functionName)) {
                if (exactMatch) {
                    if (Objects.equals(invocation.functionArgument, argument)) {
                        invocation.verified = true;
                        matchesFound += 1;
                    }
                } else {
                    boolean isSubMapResult = isSubMap(argument, invocation.functionArgument);
                    if (isSubMapResult) {
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

        final Map.Entry<String, Object> verifyTimesEntry = verificationTimes.entrySet().stream().findAny().get();
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
            return Map.of("Ok_", Map.of());
        }

        return Map.of("ErrorVerificationFailure", Map.of("reason", verificationFailurePseudoJson));
    }
}
