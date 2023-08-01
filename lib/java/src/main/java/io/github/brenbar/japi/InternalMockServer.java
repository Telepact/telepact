package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.Base64;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.TreeMap;

import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.brenbar.japi.MockVerification.AtLeastNumberOfTimes;
import io.github.brenbar.japi.MockVerification.AtMostNumberOfTimes;
import io.github.brenbar.japi.MockVerification.ExactNumberOfTimes;
import io.github.brenbar.japi.MockVerification.VerificationTimes;

class InternalMockServer {

    static Map<String, Object> handle(Context context, Map<String, Object> argument) {

        var stubs = (List<MockStub>) context.requestHeaders.get("_mockStubs");
        var invocations = (List<Invocation>) context.requestHeaders.get("_mockInvocations");
        var random = (MockRandom) context.requestHeaders.get("_mockRandom");
        var jApiSchema = (JApiSchema) context.requestHeaders.get("_mockJApiSchema");
        var enableGeneratedDefaultStub = (Boolean) context.requestHeaders.get("_mockEnableGeneratedDefaultStub");
        var enableGenerationStub = (Boolean) context.requestHeaders.getOrDefault("_mockEnableGeneratedStub", false);

        switch (context.functionName) {
            case "fn._createStub" -> {
                var whenFunction = (String) argument.get("whenFunction");
                var whenArgument = (Map<String, Object>) argument.get("whenArgument");
                var thenResult = (Map<String, Object>) argument
                        .get("thenResult");
                var allowArgumentPartialMatch = !((Boolean) argument.getOrDefault("strictMatch", true));
                var randomFillMissingResultFields = (Boolean) argument.getOrDefault("generateMissingResultFields",
                        false);

                var stub = new MockStub(whenFunction, new TreeMap<>(whenArgument), thenResult);
                if (allowArgumentPartialMatch) {
                    stub.setAllowArgumentPartialMatch(allowArgumentPartialMatch);
                }
                if (randomFillMissingResultFields) {
                    stub.setGenerateMissingResultFields(randomFillMissingResultFields);
                }

                stubs.add(0, stub);
                return Map.of("ok", Map.of());
            }
            case "fn._verify" -> {
                var verifyFunctionName = (String) argument.get("function");
                var verifyArgument = (Map<String, Object>) argument.get("argument");
                var verifyTimes = (Map<String, Object>) argument.getOrDefault("times",
                        Map.of("atLeast", Map.of("times", 1)));
                var allowArgumentPartialMatch = !((Boolean) argument.getOrDefault("strictMatch", true));

                var verificationTimes = parseFromPseudoJson(verifyTimes);

                return verify(verifyFunctionName, verifyArgument, allowArgumentPartialMatch, verificationTimes,
                        invocations);
            }
            case "fn._verifyNoMoreInteractions" -> {
                return verifyNoMoreInteractions(invocations);
            }
            case "fn._clearInvocations" -> {
                invocations.clear();
                return Map.of("ok", Map.of());
            }
            case "fn._clearStubs" -> {
                stubs.clear();
                return Map.of("ok", Map.of());
            }
            default -> {
                invocations.add(new Invocation(context.functionName, new TreeMap<>(argument)));

                for (var stub : stubs) {
                    if (Objects.equals(stub.whenFunction, context.functionName)) {
                        if (stub.allowArgumentPartialMatch) {
                            if (isSubMap(stub.whenArgument, argument)) {
                                return stub.thenResult;
                            }
                        } else {
                            if (Objects.equals(stub.whenArgument, argument)) {
                                return stub.thenResult;
                            }
                        }
                    }
                }

                if (!enableGeneratedDefaultStub && !enableGenerationStub) {
                    return Map.of("err", Map.of("_noMatchingStub", Map.of()));
                }

                var definition = jApiSchema.parsed.get(context.functionName);

                if (definition instanceof FunctionDefinition f) {
                    var okStructRef = (EnumStruct) f.resultEnum.values.get("ok");
                    var randomOkStruct = constructRandomStruct(okStructRef.fields, random);
                    return Map.of("ok", randomOkStruct);
                } else {
                    throw new JApiProcessError("Unexpected unknown function: %s".formatted(context.functionName));
                }
            }
        }
    }

    static VerificationTimes parseFromPseudoJson(Map<String, Object> verifyTimes) {
        var verifyTimesEntry = verifyTimes.entrySet().stream().findAny().get();
        var verifyTimesStruct = (Map<String, Object>) verifyTimesEntry.getValue();
        return switch (verifyTimesEntry.getKey()) {
            case "unlimited" -> new MockVerification.UnlimitedNumberOfTimes();
            case "exact" -> {
                var times = (Integer) verifyTimesStruct.get("times");
                yield new MockVerification.ExactNumberOfTimes(times);
            }
            case "atMost" -> {
                var times = (Integer) verifyTimesStruct.get("times");
                yield new MockVerification.AtMostNumberOfTimes(times);
            }
            case "atLeast" -> {
                var times = (Integer) verifyTimesStruct.get("times");
                yield new MockVerification.AtLeastNumberOfTimes(times);
            }
            default -> throw new JApiProcessError("Unknown verification times");
        };
    }

    static boolean isSubMap(Map<String, Object> sub, Map<String, Object> reference) {
        for (var subKey : sub.keySet()) {
            var referenceValue = reference.get(subKey);
            var subValue = sub.get(subKey);
            var entryIsEqual = isSubMapEntryEqual(subValue, referenceValue);
            if (!entryIsEqual) {
                return false;
            }
        }
        return true;
    }

    private static boolean isSubMapEntryEqual(Object reference, Object actual) {
        if (reference instanceof Map m1 && actual instanceof Map m2) {
            return isSubMap(m1, m2);
        } else if (reference instanceof List referenceList && actual instanceof List actualList) {
            for (int i = 0; i < referenceList.size(); i += 1) {
                var referenceElement = referenceList.get(i);
                var actualElement = actualList.get(i);
                var isEqual = isSubMapEntryEqual(referenceElement, actualElement);
                if (!isEqual) {
                    return false;
                }
            }
        }
        return Objects.equals(reference, actual);
    }

    private static Map<String, Object> constructRandomStruct(
            Map<String, FieldDeclaration> referenceStruct, MockRandom random) {

        var sortedReferenceStruct = new ArrayList<>(referenceStruct.entrySet());
        Collections.sort(sortedReferenceStruct, (e1, e2) -> e1.getKey().compareTo(e2.getKey()));

        var obj = new TreeMap<String, Object>();
        for (var field : sortedReferenceStruct) {
            var fieldDeclaration = field.getValue();
            if (fieldDeclaration.optional && random.nextBoolean()) {
                continue;
            }
            obj.put(field.getKey(), constructRandomType(fieldDeclaration.typeDeclaration, random));
        }
        return obj;
    }

    private static Object constructRandomType(TypeDeclaration typeDeclaration, MockRandom random) {
        if (typeDeclaration.nullable && random.nextBoolean()) {
            return null;
        } else if (typeDeclaration.type instanceof JsonBoolean b) {
            return random.nextBoolean();
        } else if (typeDeclaration.type instanceof JsonInteger i) {
            return random.nextInt();
        } else if (typeDeclaration.type instanceof JsonNumber n) {
            return random.nextDouble();
        } else if (typeDeclaration.type instanceof JsonString s) {
            return random.nextString();
        } else if (typeDeclaration.type instanceof JsonArray a) {
            var length = random.nextInt(3);
            var array = new ArrayList<Object>();
            for (int i = 0; i < length; i += 1) {
                array.add(constructRandomType(a.nestedType, random));
            }
            return array;
        } else if (typeDeclaration.type instanceof JsonObject o) {
            var length = random.nextInt(3);
            var obj = new TreeMap<String, Object>();
            for (int i = 0; i < length; i += 1) {
                var key = random.nextString();
                obj.put(key, constructRandomType(o.nestedType, random));
            }
            return obj;
        } else if (typeDeclaration.type instanceof JsonAny a) {
            var selectType = random.nextInt(3);
            if (selectType == 0) {
                return random.nextBoolean();
            } else if (selectType == 1) {
                return random.nextInt();
            } else {
                return random.nextString();
            }
        } else if (typeDeclaration.type instanceof Struct s) {
            return constructRandomStruct(s.fields, random);
        } else if (typeDeclaration.type instanceof Enum e) {
            return constructRandomEnum(e.values, random);
        }

        return null;
    }

    private static Map<String, Object> constructRandomEnum(Map<String, EnumType> enumValuesReference,
            MockRandom random) {
        var sortedEnumValuesReference = new ArrayList<>(enumValuesReference.entrySet());
        Collections.sort(sortedEnumValuesReference, (e1, e2) -> e1.getKey().compareTo(e2.getKey()));

        var randomIndex = random.nextInt(sortedEnumValuesReference.size());
        var enumEntry = sortedEnumValuesReference.get(randomIndex);

        var enumValue = enumEntry.getKey();
        var enumData = enumEntry.getValue();

        if (enumData instanceof EnumNesting m) {
            return Map.of(enumValue, constructRandomEnum(m.values, random));
        } else if (enumData instanceof EnumStruct es) {
            return Map.of(enumValue,
                    constructRandomStruct(es.fields, random));
        } else {
            throw new JApiProcessError("Unexpected enum data type");
        }
    }

    static Map<String, Object> verify(String functionName, Map<String, Object> argument, boolean exactMatch,
            VerificationTimes verificationTimes, List<Invocation> invocations) {
        try {
            var objectMapper = new ObjectMapper();
            var matchesFound = 0;
            for (var invocation : invocations) {
                if (Objects.equals(invocation.functionName, functionName)) {
                    if (exactMatch) {
                        if (Objects.equals(invocation.functionArgument, argument)) {
                            invocation.verified = true;
                            matchesFound += 1;
                        }
                    } else {
                        if (InternalMockServer.isSubMap(argument, invocation.functionArgument)) {
                            invocation.verified = true;
                            matchesFound += 1;
                        }
                    }
                }
            }

            var matchType = exactMatch ? "exact" : "partial";
            String matchPlurality;
            String timesType;
            int times;
            boolean passed;
            if (verificationTimes instanceof ExactNumberOfTimes e) {
                timesType = "exactly";
                times = e.times;
                matchPlurality = e.times == 1 ? "match" : "matches";
                passed = matchesFound == e.times;
            } else if (verificationTimes instanceof AtMostNumberOfTimes a) {
                timesType = "at most";
                times = a.times;
                matchPlurality = a.times == 1 ? "match" : "matches";
                passed = matchesFound <= a.times;
            } else if (verificationTimes instanceof AtLeastNumberOfTimes a) {
                timesType = "at least";
                times = a.times;
                matchPlurality = a.times == 1 ? "match" : "matches";
                passed = matchesFound >= a.times;
            } else {
                throw new JApiProcessError("Unexpected verification times");
            }

            if (passed) {
                return Map.of("ok", Map.of());
            }

            String argumentJson = objectMapper.writeValueAsString(argument);

            var errorString = new StringBuilder("""
                    Wanted %s %d %s %s, but found %d.
                    Query:
                    %s %s
                    Available:
                    """.formatted(timesType, times, matchType, matchPlurality, matchesFound, functionName,
                    argumentJson));
            var functionInvocations = invocations.stream().filter(i -> Objects.equals(functionName, i.functionName))
                    .toList();
            if (functionInvocations.isEmpty()) {
                errorString.append("<none>\n");
            } else {
                for (var invocation : functionInvocations) {
                    String invocationArgumentJson = objectMapper.writeValueAsString(invocation.functionArgument);
                    errorString.append("%s %s\n".formatted(invocation.functionName, invocationArgumentJson));
                }
            }
            return Map.of("err", Map.of("_verificationFailure", Map.of("details", errorString.toString())));
        } catch (Exception ex) {
            throw new JApiProcessError(ex);
        }
    }

    static Map<String, Object> verifyNoMoreInteractions(List<Invocation> invocations) {
        try {
            var objectMapper = new ObjectMapper();
            var invocationsNotVerified = invocations.stream().filter(i -> !i.verified).toList();

            if (invocationsNotVerified.size() > 0) {
                var errorString = new StringBuilder("""
                        Expected no more interactions, but more were found.
                        Available:
                        """);
                for (var invocation : invocationsNotVerified) {
                    var invocationArgumentJson = objectMapper.writeValueAsString(invocation.functionArgument);
                    errorString.append("%s %s\n".formatted(invocation.functionName,
                            invocationArgumentJson));
                }
                return Map.of("err", Map.of("_verificationFailure", Map.of("details", errorString.toString())));
            }

            return Map.of("ok", Map.of());
        } catch (Exception ex) {
            throw new JApiProcessError(ex);
        }
    }
}
