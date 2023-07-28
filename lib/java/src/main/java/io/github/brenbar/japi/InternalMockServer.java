package io.github.brenbar.japi;

import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.Base64;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Random;

import io.github.brenbar.japi.MockServer.ExactNumberOfTimes;
import io.github.brenbar.japi.MockServer.VerificationTimes;

class InternalMockServer {

    static Map<String, Object> handle(Context context, Map<String, Object> argument, JApiSchema jaApiSchema,
            Random random, List<Mock> mocks, List<Invocation> invocations) {

        invocations.add(new Invocation(context.functionName, argument));

        for (var mock : mocks) {
            if (Objects.equals(mock.whenFunctionName, context.functionName)) {
                if (Objects.equals(mock.whenFunctionArgument, argument)) {
                    return mock.thenAnswerResult.apply(argument);
                } else if (mock.exactMatchArgument) {
                    continue;
                } else if (isSubMap(argument, mock.whenFunctionArgument)) {
                    return mock.thenAnswerResult.apply(argument);
                }
            }
        }

        var definition = jaApiSchema.parsed.get("fn.%s".formatted(context.functionName));

        if (definition instanceof FunctionDefinition f) {
            return constructRandomEnum(f.resultEnum.values, random);
        } else {
            throw new JApiError("error._UnknownFunction", Map.of());
        }
    }

    static boolean isSubMap(Map<String, Object> reference, Map<String, Object> toCheck) {
        for (var toCheckEntry : toCheck.entrySet()) {
            var toCheckKey = toCheckEntry.getKey();
            var toCheckEntryValue = toCheckEntry.getValue();
            var referenceEntryValue = reference.get(toCheckKey);
            var entryIsEqual = isSubMapEntryEqual(referenceEntryValue, toCheckEntryValue);
            if (!entryIsEqual) {
                return false;
            }
        }
        return true;
    }

    private static boolean isSubMapEntryEqual(Object reference, Object toCheck) {
        if (reference instanceof Map m1 && toCheck instanceof Map m2) {
            return isSubMap(m1, m2);
        } else if (reference instanceof List referenceList && toCheck instanceof List toCheckList) {
            for (int i = 0; i < referenceList.size(); i += 1) {
                var referenceElement = referenceList.get(i);
                var toCheckElement = toCheckList.get(i);
                var isEqual = isSubMapEntryEqual(referenceElement, toCheckElement);
                if (!isEqual) {
                    return false;
                }
            }
        }
        return Objects.equals(reference, toCheck);
    }

    private static Map<String, Object> constructRandomStruct(
            Map<String, FieldDeclaration> referenceStruct, Random random) {

        var sortedReferenceStruct = new ArrayList<>(referenceStruct.entrySet());
        Collections.sort(sortedReferenceStruct, (e1, e2) -> e1.getKey().compareTo(e2.getKey()));

        var obj = new HashMap<String, Object>();
        for (var field : sortedReferenceStruct) {
            var fieldDeclaration = field.getValue();
            if (fieldDeclaration.optional && random.nextBoolean()) {
                continue;
            }
            obj.put(field.getKey(), constructRandomType(fieldDeclaration.typeDeclaration, random));
        }
        return obj;
    }

    private static Object constructRandomType(TypeDeclaration typeDeclaration, Random random) {
        if (typeDeclaration.nullable && random.nextBoolean()) {
            return null;
        } else if (typeDeclaration.type instanceof JsonBoolean b) {
            return random.nextBoolean();
        } else if (typeDeclaration.type instanceof JsonInteger i) {
            return random.nextInt();
        } else if (typeDeclaration.type instanceof JsonNumber n) {
            return random.nextDouble();
        } else if (typeDeclaration.type instanceof JsonString s) {
            var bytes = ByteBuffer.allocate(Integer.BYTES);
            bytes.putInt(random.nextInt());
            return Base64.getEncoder().encodeToString(bytes.array());
        } else if (typeDeclaration.type instanceof JsonArray a) {
            var length = random.nextInt(3);
            var array = new ArrayList<Object>();
            for (int i = 0; i < length; i += 1) {
                array.add(constructRandomType(a.nestedType, random));
            }
            return array;
        } else if (typeDeclaration.type instanceof JsonObject o) {
            var length = random.nextInt(3);
            var obj = new HashMap<String, Object>();
            for (int i = 0; i < length; i += 1) {
                var bytes = ByteBuffer.allocate(Integer.BYTES);
                bytes.putInt(random.nextInt());
                var key = Base64.getEncoder().encodeToString(bytes.array());
                obj.put(key, constructRandomType(o.nestedType, random));
            }
            return obj;
        } else if (typeDeclaration.type instanceof Struct s) {
            return constructRandomStruct(s.fields, random);
        } else if (typeDeclaration.type instanceof Enum e) {
            return constructRandomEnum(e.values, random);
        }

        return null;
    }

    private static Map<String, Object> constructRandomEnum(Map<String, Object> enumValuesReference, Random random) {
        var sortedEnumValuesReference = new ArrayList<>(enumValuesReference.entrySet());
        Collections.sort(sortedEnumValuesReference, (e1, e2) -> e1.getKey().compareTo(e2.getKey()));

        var randomIndex = random.nextInt(sortedEnumValuesReference.size());
        var enumEntry = sortedEnumValuesReference.get(randomIndex);

        var enumValue = enumEntry.getKey();
        var enumData = enumEntry.getValue();

        if (enumData instanceof Map<?, ?> m) {
            return Map.of(enumValue, constructRandomEnum((Map<String, Object>) m, random));
        } else {
            var structReference = new HashMap<String, FieldDeclaration>();
            for (var entry : enumValuesReference.entrySet()) {
                structReference.put(entry.getKey(), (FieldDeclaration) entry.getValue());
            }
            return Map.of(enumValue,
                    constructRandomStruct(structReference, random));
        }
    }

    static void verifyPartial(String functionName, Map<String, Object> partialMatchArgument,
            VerificationTimes verificationTimes, List<Invocation> invocations) {
        var matchesFound = 0;
        for (var invocation : invocations) {
            if (Objects.equals(invocation.functionName, functionName)) {
                if (InternalMockServer.isSubMap(invocation.functionArgument, partialMatchArgument)) {
                    invocation.verified = true;
                    matchesFound += 1;
                }
            }
        }

        if (verificationTimes instanceof ExactNumberOfTimes e) {
            if (e.times != matchesFound) {
                var errorString = new StringBuilder("""
                        Wanted exactly %d partial matches, but found %d.
                        Query:
                        %s(%s)
                        """.formatted(e.times, matchesFound, functionName, partialMatchArgument));
                throw new AssertionError(errorString);
            }
        }

        if (matchesFound > 0) {
            return;
        }

        var errorString = new StringBuilder("""
                No matching invocations.
                Wanted partial match:
                %s(%s)
                Available:
                """.formatted(functionName, partialMatchArgument));
        var functionInvocations = invocations.stream().filter(i -> Objects.equals(functionName, i.functionName))
                .toList();
        if (functionInvocations.isEmpty()) {
            errorString.append("<none>");
        } else {
            for (var invocation : functionInvocations) {
                errorString.append("%s(%s)\n".formatted(invocation.functionName, invocation.functionArgument));
            }
        }
        throw new AssertionError(errorString);
    }

    static void verifyExact(String functionName, Map<String, Object> exactMatchFunctionArgument,
            VerificationTimes verificationTimes, List<Invocation> invocations) {
        var matchesFound = 0;
        for (var invocation : invocations) {
            if (Objects.equals(invocation.functionName, functionName)) {
                if (Objects.equals(invocation.functionArgument, exactMatchFunctionArgument)) {
                    invocation.verified = true;
                    matchesFound += 1;
                }
            }
        }

        if (verificationTimes instanceof ExactNumberOfTimes e) {
            if (e.times != matchesFound) {
                var errorString = new StringBuilder("""
                        Wanted exactly %d exact matches, but found %d.
                        Query:
                        %s(%s)
                        """.formatted(e.times, matchesFound, functionName, exactMatchFunctionArgument));
                throw new AssertionError(errorString);
            }
        }

        if (matchesFound > 0) {
            return;
        }

        var errorString = new StringBuilder("""
                No matching invocations.
                Wanted exact match:
                %s(%s)
                Available:
                """.formatted(functionName, exactMatchFunctionArgument));
        var functionInvocations = invocations.stream().filter(i -> Objects.equals(functionName, i.functionName))
                .toList();
        if (functionInvocations.isEmpty()) {
            errorString.append("<none>");
        } else {
            for (var invocation : functionInvocations) {
                errorString.append("%s(%s)\n".formatted(invocation.functionName, invocation.functionArgument));
            }
        }
        throw new AssertionError(errorString);
    }

    static void verifyNoMoreInteractions(List<Invocation> invocations) {
        var invocationsNotVerified = invocations.stream().filter(i -> !i.verified).toList();

        if (invocationsNotVerified.size() > 0) {
            var errorString = new StringBuilder("""
                    Expected no more interactions, but more were found.
                    Available:
                    """);
            for (var invocation : invocationsNotVerified) {
                errorString.append("%s(%s)\n".formatted(invocation.functionName, invocation.functionArgument));
            }
            throw new AssertionError(errorString);
        }
    }
}
