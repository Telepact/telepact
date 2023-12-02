package io.github.brenbar.japi;

import java.util.ArrayList;
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

class _MockServerUtil {

    static Message handle(Message requestMessage, List<MockStub> stubs,
            List<Invocation> invocations, MockRandom random, JApiSchema jApiSchema,
            boolean enableGeneratedDefaultStub) {

        var enableGenerationStub = (Boolean) requestMessage.header.getOrDefault("_mockEnableGeneratedStub", false);
        var functionName = requestMessage.getBodyTarget();
        var argument = requestMessage.getBodyPayload();

        switch (functionName) {
            case "fn._createStub" -> {
                var givenStub = (Map<String, Object>) argument.get("stub");

                var stubCall = givenStub.entrySet().stream().filter(e -> e.getKey().startsWith("fn."))
                        .findAny().get();
                var stubFunctionName = stubCall.getKey();
                var stubArg = (Map<String, Object>) stubCall.getValue();
                var stubResult = (Map<String, Object>) givenStub.get("->");
                var allowArgumentPartialMatch = !((Boolean) argument.getOrDefault("strictMatch", false));

                var stub = new MockStub(stubFunctionName, new TreeMap<>(stubArg), stubResult);
                if (allowArgumentPartialMatch) {
                    stub.setAllowArgumentPartialMatch(allowArgumentPartialMatch);
                }

                stubs.add(0, stub);
                return new Message(Map.of("ok", Map.of()));
            }
            case "fn._verify" -> {
                var givenCall = (Map<String, Object>) argument.get("call");

                var call = givenCall.entrySet().stream().filter(e -> e.getKey().startsWith("fn."))
                        .findAny().get();
                var callFunctionName = call.getKey();
                var callArg = (Map<String, Object>) call.getValue();
                var verifyTimes = (Map<String, Object>) argument.getOrDefault("count",
                        Map.of("atLeast", Map.of("times", 1)));
                var strictMatch = (Boolean) argument.getOrDefault("strictMatch", false);

                var verificationTimes = parseFromPseudoJson(verifyTimes);

                var verificationResult = verify(callFunctionName, callArg, strictMatch,
                        verificationTimes,
                        invocations);
                return new Message(verificationResult);
            }
            case "fn._verifyNoMoreInteractions" -> {
                var verificationResult = verifyNoMoreInteractions(invocations);
                return new Message(verificationResult);
            }
            case "fn._clearCalls" -> {
                invocations.clear();
                return new Message(Map.of("ok", Map.of()));
            }
            case "fn._clearStubs" -> {
                stubs.clear();
                return new Message(Map.of("ok", Map.of()));
            }
            default -> {
                invocations.add(new Invocation(functionName, new TreeMap<>(argument)));

                var definition = (Fn) jApiSchema.parsed.get(functionName);

                for (var stub : stubs) {
                    if (Objects.equals(stub.whenFunction, functionName)) {
                        if (stub.allowArgumentPartialMatch) {
                            if (isSubMap(stub.whenArgument, argument)) {
                                var includeRandomOptionalFields = false;
                                var result = constructRandomEnum(definition.result.values, stub.thenResult,
                                        includeRandomOptionalFields, random);
                                return new Message(result);
                            }
                        } else {
                            if (Objects.equals(stub.whenArgument, argument)) {
                                var includeRandomOptionalFields = false;
                                var result = constructRandomEnum(definition.result.values, stub.thenResult,
                                        includeRandomOptionalFields, random);
                                return new Message(result);
                            }
                        }
                    }
                }

                if (!enableGeneratedDefaultStub && !enableGenerationStub) {
                    return new Message(Map.of("_errorNoMatchingStub", Map.of()));
                }

                if (definition != null) {
                    var resultEnum = (Enum) definition.result;
                    var okStructRef = resultEnum.values.get("ok");
                    var includeRandomOptionalFields = true;
                    var randomOkStruct = constructRandomStruct(okStructRef.fields, new HashMap<>(),
                            includeRandomOptionalFields, random);
                    return new Message(Map.of("ok", randomOkStruct));
                } else {
                    throw new JApiProcessError("Unexpected unknown function: %s".formatted(functionName));
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

    static boolean isSubMap(Map<String, Object> part, Map<String, Object> whole) {
        for (var partKey : part.keySet()) {
            var wholeValue = whole.get(partKey);
            var partValue = part.get(partKey);
            var entryIsEqual = isSubMapEntryEqual(partValue, wholeValue);
            if (!entryIsEqual) {
                return false;
            }
        }
        return true;
    }

    private static boolean isSubMapEntryEqual(Object partValue, Object wholeValue) {
        if (partValue instanceof Map m1 && wholeValue instanceof Map m2) {
            return isSubMap(m1, m2);
        } else if (partValue instanceof List partList && wholeValue instanceof List wholeList) {
            for (int i = 0; i < partList.size(); i += 1) {
                var partElement = partList.get(i);
                var partMatches = false;
                for (var wholeElement : wholeList) {
                    if (isSubMapEntryEqual(partElement, wholeElement)) {
                        partMatches = true;
                        break;
                    }
                }
                if (!partMatches) {
                    return false;
                }
            }
            return true;
        } else {
            return Objects.equals(partValue, wholeValue);
        }
    }

    private static Map<String, Object> constructRandomStruct(
            Map<String, FieldDeclaration> referenceStruct, Map<String, Object> startingStruct,
            boolean includeRandomOptionalFields, MockRandom random) {

        var sortedReferenceStruct = new ArrayList<>(referenceStruct.entrySet());
        Collections.sort(sortedReferenceStruct, (e1, e2) -> e1.getKey().compareTo(e2.getKey()));

        var obj = new TreeMap<String, Object>();
        for (var field : sortedReferenceStruct) {
            var fieldName = field.getKey();
            var fieldDeclaration = field.getValue();
            var startingValue = startingStruct.get(fieldName);
            var useStartingValue = startingStruct.containsKey(fieldName);
            Object value;
            if (useStartingValue) {
                value = constructRandomType(fieldDeclaration.typeDeclaration, startingValue, useStartingValue,
                        includeRandomOptionalFields, random);
            } else {
                if (!fieldDeclaration.optional) {
                    value = constructRandomType(fieldDeclaration.typeDeclaration, null, false,
                            includeRandomOptionalFields,
                            random);
                } else {
                    if (!includeRandomOptionalFields) {
                        continue;
                    }
                    if (random.nextBoolean()) {
                        continue;
                    }
                    value = constructRandomType(fieldDeclaration.typeDeclaration, null, false,
                            includeRandomOptionalFields,
                            random);
                }
            }
            obj.put(fieldName, value);
        }
        return obj;
    }

    private static Object constructRandomType(TypeDeclaration typeDeclaration, Object startingValue,
            boolean useStartingValue,
            boolean includeRandomOptionalFields,
            MockRandom random) {

        if (typeDeclaration.nullable && !useStartingValue && random.nextBoolean()) {
            return null;
        } else if (typeDeclaration.type instanceof JsonBoolean b) {
            if (useStartingValue) {
                return startingValue;
            } else {
                return random.nextBoolean();
            }
        } else if (typeDeclaration.type instanceof JsonInteger i) {
            if (useStartingValue) {
                return startingValue;
            } else {
                return random.nextInt();
            }
        } else if (typeDeclaration.type instanceof JsonNumber n) {
            if (useStartingValue) {
                return startingValue;
            } else {
                return random.nextDouble();
            }
        } else if (typeDeclaration.type instanceof JsonString s) {
            if (useStartingValue) {
                return startingValue;
            } else {
                return random.nextString();
            }
        } else if (typeDeclaration.type instanceof JsonArray a) {
            var nestedType = typeDeclaration.typeParameters.get(0);
            if (useStartingValue) {
                var startingArray = (List<Object>) startingValue;
                var array = new ArrayList<Object>();
                for (var startingArrayValue : startingArray) {
                    var value = constructRandomType(nestedType, startingArrayValue, true,
                            includeRandomOptionalFields,
                            random);
                    array.add(value);
                }
                return array;
            } else {
                var length = random.nextInt(3);
                var array = new ArrayList<Object>();
                for (int i = 0; i < length; i += 1) {
                    var value = constructRandomType(nestedType, null, false, includeRandomOptionalFields, random);
                    array.add(value);
                }
                return array;
            }
        } else if (typeDeclaration.type instanceof JsonObject o) {
            var nestedType = typeDeclaration.typeParameters.get(0);
            if (useStartingValue) {
                var startingObj = (Map<String, Object>) startingValue;
                var obj = new TreeMap<String, Object>();
                for (var startingObjEntry : startingObj.entrySet()) {
                    var key = startingObjEntry.getKey();
                    var startingObjValue = startingObjEntry.getValue();
                    var value = constructRandomType(nestedType, startingObjValue, true, includeRandomOptionalFields,
                            random);
                    obj.put(key, value);
                }
                return obj;
            } else {
                var length = random.nextInt(3);
                var obj = new TreeMap<String, Object>();
                for (int i = 0; i < length; i += 1) {
                    var key = random.nextString();
                    var value = constructRandomType(nestedType, null, false, includeRandomOptionalFields, random);
                    obj.put(key, value);
                }
                return obj;
            }
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
            if (useStartingValue) {
                var startingStructValue = (Map<String, Object>) startingValue;
                return constructRandomStruct(s.fields, startingStructValue, includeRandomOptionalFields, random);
            } else {
                return constructRandomStruct(s.fields, new HashMap<>(), includeRandomOptionalFields, random);
            }
        } else if (typeDeclaration.type instanceof Enum e) {
            if (useStartingValue) {
                var startingEnumValue = (Map<String, Object>) startingValue;
                return constructRandomEnum(e.values, startingEnumValue, includeRandomOptionalFields, random);
            } else {
                return constructRandomEnum(e.values, new HashMap<>(), includeRandomOptionalFields, random);
            }
        } else if (typeDeclaration.type instanceof Fn f) {
            if (useStartingValue) {
                var startingFnValue = (Map<String, Object>) startingValue;
                return constructRandomStruct(f.arg.fields, startingFnValue, includeRandomOptionalFields, random);
            } else {
                return constructRandomStruct(f.arg.fields, new HashMap<>(), includeRandomOptionalFields, random);
            }
        } else {
            throw new RuntimeException("Unexpected type: %s".formatted(typeDeclaration.type));
        }
    }

    private static Map<String, Object> constructRandomEnum(Map<String, Struct> enumValuesReference,
            Map<String, Object> startingEnum,
            boolean includeRandomOptionalFields,
            MockRandom random) {
        var existingEnumValue = startingEnum.keySet().stream().findAny();
        if (existingEnumValue.isPresent()) {
            var enumValue = existingEnumValue.get();
            var enumStructType = enumValuesReference.get(enumValue);
            var enumStartingStruct = (Map<String, Object>) startingEnum.get(enumValue);

            return Map.of(enumValue, constructRandomStruct(enumStructType.fields, enumStartingStruct,
                    includeRandomOptionalFields, random));
        } else {
            var sortedEnumValuesReference = new ArrayList<>(enumValuesReference.entrySet());
            Collections.sort(sortedEnumValuesReference, (e1, e2) -> e1.getKey().compareTo(e2.getKey()));

            var randomIndex = random.nextInt(sortedEnumValuesReference.size());
            var enumEntry = sortedEnumValuesReference.get(randomIndex);

            var enumValue = enumEntry.getKey();
            var enumData = enumEntry.getValue();

            return Map.of(enumValue,
                    constructRandomStruct(enumData.fields, new HashMap<>(), includeRandomOptionalFields, random));
        }

    }

    static Map<String, Object> verify(String functionName, Map<String, Object> argument,
            boolean exactMatch,
            VerificationTimes verificationTimes, List<Invocation> invocations) {
        var matchesFound = 0;
        for (var invocation : invocations) {
            if (Objects.equals(invocation.functionName, functionName)) {
                if (exactMatch) {
                    if (Objects.equals(invocation.functionArgument, argument)) {
                        invocation.verified = true;
                        matchesFound += 1;
                    }
                } else {
                    if (_MockServerUtil.isSubMap(argument, invocation.functionArgument)) {
                        invocation.verified = true;
                        matchesFound += 1;
                    }
                }
            }
        }

        var allCallsPseudoJson = new ArrayList<Map<String, Object>>();
        for (var invocation : invocations) {
            allCallsPseudoJson.add(Map.of(invocation.functionName, invocation.functionArgument));
        }
        Map<String, Object> verificationFailurePseudoJson = null;
        if (verificationTimes instanceof ExactNumberOfTimes e) {
            if (matchesFound > e.times) {
                verificationFailurePseudoJson = Map.of("tooManyMatchingCalls",
                        new TreeMap<>(Map.ofEntries(
                                Map.entry("wanted", Map.of("exact", Map.of("times", e.times))),
                                Map.entry("found", matchesFound),
                                Map.entry("allCalls", allCallsPseudoJson))));
            } else if (matchesFound < e.times) {
                verificationFailurePseudoJson = Map.of("tooFewMatchingCalls",
                        new TreeMap<>(Map.ofEntries(
                                Map.entry("wanted", Map.of("exact", Map.of("times", e.times))),
                                Map.entry("found", matchesFound),
                                Map.entry("allCalls", allCallsPseudoJson))));
            }
        } else if (verificationTimes instanceof AtMostNumberOfTimes a) {
            if (matchesFound > a.times) {
                verificationFailurePseudoJson = Map.of("tooManyMatchingCalls",
                        new TreeMap<>(Map.ofEntries(
                                Map.entry("wanted", Map.of("atMost", Map.of("times", a.times))),
                                Map.entry("found", matchesFound),
                                Map.entry("allCalls", allCallsPseudoJson))));
            }
        } else if (verificationTimes instanceof AtLeastNumberOfTimes a) {
            if (matchesFound < a.times) {
                verificationFailurePseudoJson = Map.of("tooFewMatchingCalls",
                        new TreeMap<>(Map.ofEntries(
                                Map.entry("wanted", Map.of("atLeast", Map.of("times", a.times))),
                                Map.entry("found", matchesFound),
                                Map.entry("allCalls", allCallsPseudoJson))));

            }
        } else {
            throw new JApiProcessError("Unexpected verification times");
        }

        if (verificationFailurePseudoJson == null) {
            return Map.of("ok", Map.of());
        }

        return Map.of("errorVerificationFailure", Map.of("reason", verificationFailurePseudoJson));
    }

    static Map<String, Object> verifyNoMoreInteractions(List<Invocation> invocations) {
        var invocationsNotVerified = invocations.stream().filter(i -> !i.verified).toList();

        if (invocationsNotVerified.size() > 0) {
            var unverifiedCallsPseudoJson = new ArrayList<Map<String, Object>>();
            for (var invocation : invocationsNotVerified) {
                unverifiedCallsPseudoJson.add(Map.of(invocation.functionName, invocation.functionArgument));
            }
            return Map.of("errorVerificationFailure",
                    Map.of("additionalUnverifiedCalls", unverifiedCallsPseudoJson));
        }

        return Map.of("ok", Map.of());
    }
}
