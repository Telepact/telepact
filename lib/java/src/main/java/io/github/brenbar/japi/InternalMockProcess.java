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

class InternalMockProcess {

    static Map<String, Object> handle(Context context, Map<String, Object> input, Map<String, Definition> jApi,
            Random random, List<Mock> mocks, List<Invocation> invocations) {

        invocations.add(new Invocation(context.functionName, input));

        for (var mock : mocks) {
            if (Objects.equals(mock.whenFunctionName, context.functionName)) {
                if (Objects.equals(mock.whenFunctionInput, input)) {
                    return mock.thenAnswerOutput.apply(input);
                } else if (mock.exactMatchInput) {
                    continue;
                } else if (isSubMap(input, mock.whenFunctionInput)) {
                    return mock.thenAnswerOutput.apply(input);
                }
            }
        }

        var definition = jApi.get("function.%s".formatted(context.functionName));

        if (definition instanceof FunctionDefinition f) {
            return constructRandomStruct(f.outputStruct.fields, random);
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

        var obj = new HashMap<String, Object>();
        for (var field : referenceStruct.entrySet()) {
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
            var enumValues = new ArrayList<>(e.values.entrySet());
            Collections.sort(enumValues, (e1, e2) -> e1.getKey().compareTo(e2.getKey()));

            var randomIndex = random.nextInt(enumValues.size());
            var enumValue = enumValues.get(randomIndex);
            var s = enumValue.getValue();

            return constructRandomStruct(s.fields, random);
        }

        return null;
    }
}
