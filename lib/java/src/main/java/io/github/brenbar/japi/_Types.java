package io.github.brenbar.japi;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.stream.Collectors;

class UFieldDeclaration {

    public final String fieldName;
    public final UTypeDeclaration typeDeclaration;
    public final boolean optional;

    public UFieldDeclaration(
            String fieldName,
            UTypeDeclaration typeDeclaration,
            boolean optional) {
        this.fieldName = fieldName;
        this.typeDeclaration = typeDeclaration;
        this.optional = optional;
    }
}

class UTypeDeclaration {
    public final UType type;
    public final boolean nullable;
    public final List<UTypeDeclaration> typeParameters;

    public UTypeDeclaration(
            UType type,
            boolean nullable, List<UTypeDeclaration> typeParameters) {
        this.type = type;
        this.nullable = nullable;
        this.typeParameters = typeParameters;
    }

    public List<ValidationFailure> validate(Object value, List<UTypeDeclaration> generics) {
        if (value == null) {
            var isNullable = this.type instanceof UGeneric g
                    ? generics.get(g.index).nullable
                    : this.nullable;
            if (!isNullable) {
                return _ValidateUtil.getTypeUnexpectedValidationFailure(List.of(), value,
                        this.type.getName(generics));
            } else {
                return Collections.emptyList();
            }
        } else {
            return this.type.validate(value, this.typeParameters, generics);
        }
    }

    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<UTypeDeclaration> generics,
            RandomGenerator random) {
        if (this.nullable && !useStartingValue && random.nextBoolean()) {
            return null;
        } else {
            return this.type.generateRandomValue(startingValue, useStartingValue, includeRandomOptionalFields,
                    this.typeParameters, generics, random);
        }
    }
}

interface UType {
    public int getTypeParameterCount();

    public List<ValidationFailure> validate(Object value, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics);

    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics,
            RandomGenerator random);

    public String getName(List<UTypeDeclaration> generics);
}

class UBoolean implements UType {

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics) {
        if (value instanceof Boolean) {
            return Collections.emptyList();
        } else {
            return _ValidateUtil.getTypeUnexpectedValidationFailure(List.of(), value,
                    this.getName(generics));
        }
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics,
            RandomGenerator random) {
        if (useStartingValue) {
            return startingValue;
        } else {
            return random.nextBoolean();
        }
    }

    @Override
    public String getName(List<UTypeDeclaration> generics) {
        return "Boolean";
    }

}

class UInteger implements UType {
    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics) {
        if (value instanceof Long || value instanceof Integer) {
            return Collections.emptyList();
        } else if (value instanceof BigInteger bi || value instanceof BigDecimal bd) {
            return Collections.singletonList(
                    new ValidationFailure(new ArrayList<Object>(), "NumberOutOfRange", Map.of()));
        } else {
            return _ValidateUtil.getTypeUnexpectedValidationFailure(List.of(), value,
                    this.getName(generics));
        }
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics,
            RandomGenerator random) {
        if (useStartingValue) {
            return startingValue;
        } else {
            return random.nextInt();
        }
    }

    @Override
    public String getName(List<UTypeDeclaration> generics) {
        return "Integer";
    }
}

class UNumber implements UType {
    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics) {
        if (value instanceof BigInteger bi || value instanceof BigDecimal bd) {
            return Collections.singletonList(
                    new ValidationFailure(new ArrayList<Object>(), "NumberOutOfRange", Map.of()));
        } else if (value instanceof Number) {
            return Collections.emptyList();
        } else {
            return _ValidateUtil.getTypeUnexpectedValidationFailure(List.of(), value,
                    this.getName(generics));
        }
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics,
            RandomGenerator random) {
        if (useStartingValue) {
            return startingValue;
        } else {
            return random.nextDouble();
        }
    }

    @Override
    public String getName(List<UTypeDeclaration> generics) {
        return "Number";
    }
}

class UString implements UType {
    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics) {
        if (value instanceof String) {
            return Collections.emptyList();
        } else {
            return _ValidateUtil.getTypeUnexpectedValidationFailure(List.of(), value,
                    this.getName(generics));
        }
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics,
            RandomGenerator random) {
        if (useStartingValue) {
            return startingValue;
        } else {
            return random.nextString();
        }
    }

    @Override
    public String getName(List<UTypeDeclaration> generics) {
        return "String";
    }
}

class UArray implements UType {

    @Override
    public int getTypeParameterCount() {
        return 1;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics) {
        if (value instanceof List l) {
            var nestedTypeDeclaration = typeParameters.get(0);
            var validationFailures = new ArrayList<ValidationFailure>();
            for (var i = 0; i < l.size(); i += 1) {
                var element = l.get(i);
                var nestedValidationFailures = nestedTypeDeclaration.validate(element, generics);
                final var index = i;
                var nestedValidationFailuresWithPath = nestedValidationFailures
                        .stream()
                        .map(f -> new ValidationFailure(_ValidateUtil.prepend(index, f.path), f.reason,
                                f.data))
                        .toList();
                validationFailures.addAll(nestedValidationFailuresWithPath);
            }
            return validationFailures;
        } else {
            return _ValidateUtil.getTypeUnexpectedValidationFailure(List.of(), value,
                    this.getName(generics));
        }
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics,
            RandomGenerator random) {
        var nestedTypeDeclaration = typeParameters.get(0);
        if (useStartingValue) {
            var startingArray = (List<Object>) startingValue;
            var array = new ArrayList<Object>();
            for (var startingArrayValue : startingArray) {
                var value = nestedTypeDeclaration.generateRandomValue(startingArrayValue, true,
                        includeRandomOptionalFields, generics, random);
                array.add(value);
            }
            return array;
        } else {
            var length = random.nextInt(3);
            var array = new ArrayList<Object>();
            for (int i = 0; i < length; i += 1) {
                var value = nestedTypeDeclaration.generateRandomValue(null, false,
                        includeRandomOptionalFields,
                        generics, random);
                array.add(value);
            }
            return array;
        }
    }

    @Override
    public String getName(List<UTypeDeclaration> generics) {
        return "Array";
    }
}

class UObject implements UType {

    @Override
    public int getTypeParameterCount() {
        return 1;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics) {
        if (value instanceof Map<?, ?> m) {
            var nestedTypeDeclaration = typeParameters.get(0);
            var validationFailures = new ArrayList<ValidationFailure>();
            for (Map.Entry<?, ?> entry : m.entrySet()) {
                var k = (String) entry.getKey();
                var v = entry.getValue();
                var nestedValidationFailures = nestedTypeDeclaration.validate(v, generics);
                var nestedValidationFailuresWithPath = nestedValidationFailures
                        .stream()
                        .map(f -> new ValidationFailure(_ValidateUtil.prepend(k, f.path), f.reason, f.data))
                        .toList();
                validationFailures.addAll(nestedValidationFailuresWithPath);
            }
            return validationFailures;
        } else {
            return _ValidateUtil.getTypeUnexpectedValidationFailure(List.of(), value,
                    this.getName(generics));
        }
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics,
            RandomGenerator random) {
        var nestedTypeDeclaration = typeParameters.get(0);
        if (useStartingValue) {
            var startingObj = (Map<String, Object>) startingValue;
            var obj = new TreeMap<String, Object>();
            for (var startingObjEntry : startingObj.entrySet()) {
                var key = startingObjEntry.getKey();
                var startingObjValue = startingObjEntry.getValue();
                var value = nestedTypeDeclaration.generateRandomValue(startingObjValue, true,
                        includeRandomOptionalFields, generics, random);
                obj.put(key, value);
            }
            return obj;
        } else {
            var length = random.nextInt(3);
            var obj = new TreeMap<String, Object>();
            for (int i = 0; i < length; i += 1) {
                var key = random.nextString();
                var value = nestedTypeDeclaration.generateRandomValue(null, false, includeRandomOptionalFields,
                        generics, random);
                obj.put(key, value);
            }
            return obj;
        }
    }

    @Override
    public String getName(List<UTypeDeclaration> generics) {
        return "Object";
    }

}

class UAny implements UType {
    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics) {
        return List.of();
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics,
            RandomGenerator random) {
        var selectType = random.nextInt(3);
        if (selectType == 0) {
            return random.nextBoolean();
        } else if (selectType == 1) {
            return random.nextInt();
        } else {
            return random.nextString();
        }
    }

    @Override
    public String getName(List<UTypeDeclaration> generics) {
        return "Any";
    }
}

class UGeneric implements UType {
    public final int index;

    public UGeneric(int index) {
        this.index = index;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics) {
        var typeDeclaration = generics.get(this.index);
        return typeDeclaration.validate(value, List.of());
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics,
            RandomGenerator random) {
        var genericTypeDeclaration = generics.get(this.index);
        return genericTypeDeclaration.generateRandomValue(startingValue, useStartingValue,
                includeRandomOptionalFields, List.of(), random);
    }

    @Override
    public String getName(List<UTypeDeclaration> generics) {
        var typeDeclaration = generics.get(this.index);
        return typeDeclaration.type.getName(generics);
    }
}

class UStruct implements UType {

    public final String name;
    public final Map<String, UFieldDeclaration> fields;
    public final int typeParameterCount;

    public UStruct(String name, Map<String, UFieldDeclaration> fields, int typeParameterCount) {
        this.name = name;
        this.fields = fields;
        this.typeParameterCount = typeParameterCount;
    }

    @Override
    public int getTypeParameterCount() {
        return this.typeParameterCount;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics) {
        if (value instanceof Map<?, ?> m) {
            return validateStructFields(this.fields, (Map<String, Object>) m, typeParameters);
        } else {
            return _ValidateUtil.getTypeUnexpectedValidationFailure(List.of(), value,
                    this.getName(generics));
        }
    }

    public static List<ValidationFailure> validateStructFields(
            Map<String, UFieldDeclaration> fields,
            Map<String, Object> actualStruct, List<UTypeDeclaration> typeParameters) {
        var validationFailures = new ArrayList<ValidationFailure>();

        var missingFields = new ArrayList<String>();
        for (Map.Entry<String, UFieldDeclaration> entry : fields.entrySet()) {
            var fieldName = entry.getKey();
            var fieldDeclaration = entry.getValue();
            if (!actualStruct.containsKey(fieldName) && !fieldDeclaration.optional) {
                missingFields.add(fieldName);
            }
        }

        for (var missingField : missingFields) {
            var validationFailure = new ValidationFailure(List.of(missingField),
                    "RequiredStructFieldMissing", Map.of());
            validationFailures
                    .add(validationFailure);
        }

        for (Map.Entry<String, Object> entry : actualStruct.entrySet()) {
            var fieldName = entry.getKey();
            var fieldValue = entry.getValue();
            var referenceField = fields.get(fieldName);
            if (referenceField == null) {
                var validationFailure = new ValidationFailure(List.of(fieldName),
                        "StructFieldUnknown", Map.of());
                validationFailures
                        .add(validationFailure);
                continue;
            }
            var nestedValidationFailures = referenceField.typeDeclaration.validate(fieldValue, typeParameters);
            var nestedValidationFailuresWithPath = nestedValidationFailures
                    .stream()
                    .map(f -> new ValidationFailure(_ValidateUtil.prepend(fieldName, f.path), f.reason,
                            f.data))
                    .toList();
            validationFailures.addAll(nestedValidationFailuresWithPath);
        }

        return validationFailures;
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics,
            RandomGenerator random) {
        if (useStartingValue) {
            var startingStructValue = (Map<String, Object>) startingValue;
            return constructRandomStruct(this.fields, startingStructValue, includeRandomOptionalFields,
                    typeParameters, random);
        } else {
            return constructRandomStruct(this.fields, new HashMap<>(), includeRandomOptionalFields,
                    typeParameters, random);
        }
    }

    public static Map<String, Object> constructRandomStruct(
            Map<String, UFieldDeclaration> referenceStruct, Map<String, Object> startingStruct,
            boolean includeRandomOptionalFields, List<UTypeDeclaration> typeParameters,
            RandomGenerator random) {

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
                value = fieldDeclaration.typeDeclaration.generateRandomValue(startingValue, useStartingValue,
                        includeRandomOptionalFields, typeParameters,
                        random);
            } else {
                if (!fieldDeclaration.optional) {
                    value = fieldDeclaration.typeDeclaration.generateRandomValue(null, false,
                            includeRandomOptionalFields, typeParameters, random);
                } else {
                    if (!includeRandomOptionalFields) {
                        continue;
                    }
                    if (random.nextBoolean()) {
                        continue;
                    }
                    value = fieldDeclaration.typeDeclaration.generateRandomValue(null, false,
                            includeRandomOptionalFields, typeParameters, random);
                }
            }
            obj.put(fieldName, value);
        }
        return obj;
    }

    @Override
    public String getName(List<UTypeDeclaration> generics) {
        return "Object";
    }
}

class UUnion implements UType {

    public final String name;
    public final Map<String, UStruct> values;
    public final int typeParameterCount;

    public UUnion(String name, Map<String, UStruct> values, int typeParameterCount) {
        this.name = name;
        this.values = values;
        this.typeParameterCount = typeParameterCount;
    }

    @Override
    public int getTypeParameterCount() {
        return this.typeParameterCount;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics) {
        if (value instanceof Map<?, ?> m) {
            return validateUnionValues(this.values, m, typeParameters);
        } else {
            return _ValidateUtil.getTypeUnexpectedValidationFailure(List.of(), value,
                    this.getName(generics));
        }
    }

    private List<ValidationFailure> validateUnionValues(
            Map<String, UStruct> referenceValues,
            Map<?, ?> actual, List<UTypeDeclaration> typeParameters) {
        if (actual.size() != 1) {
            return Collections.singletonList(
                    new ValidationFailure(new ArrayList<Object>(),
                            "ZeroOrManyUnionFieldsDisallowed", Map.of()));
        }
        var entry = UUnion.entry((Map<String, Object>) actual);
        var unionTarget = (String) entry.getKey();
        var unionPayload = entry.getValue();

        var referenceStruct = referenceValues.get(unionTarget);
        if (referenceStruct == null) {
            return Collections
                    .singletonList(new ValidationFailure(List.of(unionTarget),
                            "UnionFieldUnknown", Map.of()));
        }

        if (unionPayload instanceof Map<?, ?> m2) {
            var nestedValidationFailures = validateUnionStruct(referenceStruct, unionTarget,
                    (Map<String, Object>) m2, typeParameters);
            var nestedValidationFailuresWithPath = nestedValidationFailures
                    .stream()
                    .map(f -> new ValidationFailure(_ValidateUtil.prepend(unionTarget, f.path), f.reason,
                            f.data))
                    .toList();
            return nestedValidationFailuresWithPath;
        } else {
            return _ValidateUtil.getTypeUnexpectedValidationFailure(List.of(unionTarget),
                    unionPayload, "Object");
        }
    }

    private static List<ValidationFailure> validateUnionStruct(
            UStruct unionStruct,
            String unionCase,
            Map<String, Object> actual, List<UTypeDeclaration> typeParameters) {
        var validationFailures = new ArrayList<ValidationFailure>();

        var nestedValidationFailures = UStruct.validateStructFields(unionStruct.fields,
                actual, typeParameters);
        validationFailures.addAll(nestedValidationFailures);

        return validationFailures;
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics,
            RandomGenerator random) {
        if (useStartingValue) {
            var startingUnionValue = (Map<String, Object>) startingValue;
            return constructRandomUnion(this.values, startingUnionValue, includeRandomOptionalFields,
                    typeParameters, random);
        } else {
            return constructRandomUnion(this.values, new HashMap<>(), includeRandomOptionalFields,
                    typeParameters, random);
        }
    }

    static Map<String, Object> constructRandomUnion(Map<String, UStruct> unionValuesReference,
            Map<String, Object> startingUnion,
            boolean includeRandomOptionalFields,
            List<UTypeDeclaration> typeParameters,
            RandomGenerator random) {
        if (!startingUnion.isEmpty()) {
            var unionEntry = UUnion.entry(startingUnion);
            var unionValue = unionEntry.getKey();
            var unionStructType = unionValuesReference.get(unionValue);
            var unionStartingStruct = (Map<String, Object>) startingUnion.get(unionValue);

            return Map.of(unionValue, UStruct.constructRandomStruct(unionStructType.fields, unionStartingStruct,
                    includeRandomOptionalFields, typeParameters, random));
        } else {
            var sortedUnionValuesReference = new ArrayList<>(unionValuesReference.entrySet());
            Collections.sort(sortedUnionValuesReference, (e1, e2) -> e1.getKey().compareTo(e2.getKey()));

            var randomIndex = random.nextInt(sortedUnionValuesReference.size());
            var unionEntry = sortedUnionValuesReference.get(randomIndex);

            var unionValue = unionEntry.getKey();
            var unionData = unionEntry.getValue();

            return Map.of(unionValue,
                    UStruct.constructRandomStruct(unionData.fields, new HashMap<>(), includeRandomOptionalFields,
                            typeParameters, random));
        }
    }

    static Map.Entry<String, Object> entry(Map<String, Object> union) {
        return union.entrySet().stream().findAny().orElse(null);
    }

    @Override
    public String getName(List<UTypeDeclaration> generics) {
        return "Object";
    }
}

class UFn implements UType {

    public final String name;
    public final UUnion call;
    public final UUnion result;

    public UFn(String name, UUnion call, UUnion output) {
        this.name = name;
        this.call = call;
        this.result = output;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics) {
        return this.call.validate(value, typeParameters, generics);
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics,
            RandomGenerator random) {
        if (useStartingValue) {
            var startingFnValue = (Map<String, Object>) startingValue;
            return UUnion.constructRandomUnion(this.call.values, startingFnValue, includeRandomOptionalFields,
                    List.of(),
                    random);
        } else {
            return UUnion.constructRandomUnion(this.call.values, new HashMap<>(), includeRandomOptionalFields,
                    List.of(),
                    random);
        }
    }

    @Override
    public String getName(List<UTypeDeclaration> generics) {
        return "Object";
    }
}

class UTrait {
    public final String name;
    public final UFn fn;
    public final String regex;

    public UTrait(String name, UFn fn, String regex) {
        this.name = name;
        this.fn = fn;
        this.regex = regex;
    }
}

class UInfo {
    public final String name;

    public UInfo(String name) {
        this.name = name;
    }
}

class UExt implements UType {
    public final String name;
    public final TypeExtension typeExtension;
    public final int typeParameterCount;

    public UExt(String name, TypeExtension typeExtension, int typeParameterCount) {
        this.name = name;
        this.typeExtension = typeExtension;
        this.typeParameterCount = typeParameterCount;
    }

    @Override
    public int getTypeParameterCount() {
        return this.typeParameterCount;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics) {
        return this.typeExtension.validate(value);
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<UTypeDeclaration> typeParameters, List<UTypeDeclaration> generics,
            RandomGenerator random) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'generateRandomValue'");
    }

    @Override
    public String getName(List<UTypeDeclaration> generics) {
        return "Any";
    }
}

class BinaryEncoding {

    public final Map<String, Long> encodeMap;
    public final Map<Long, String> decodeMap;
    public final Integer checksum;

    public BinaryEncoding(Map<String, Long> binaryEncoding, Integer checksum) {
        this.encodeMap = binaryEncoding;
        this.decodeMap = binaryEncoding.entrySet().stream()
                .collect(Collectors.toMap(e -> Long.valueOf(e.getValue()), e -> e.getKey()));
        this.checksum = checksum;
    }
}

interface BinaryEncoder {
    List<Object> encode(List<Object> message) throws BinaryEncoderUnavailableError;

    List<Object> decode(List<Object> message) throws BinaryEncoderUnavailableError;
}

class ValidationFailure {
    public final List<Object> path;
    public final String reason;
    public final Map<String, Object> data;

    public ValidationFailure(List<Object> path, String reason, Map<String, Object> data) {
        this.path = path;
        this.reason = reason;
        this.data = data;
    }
}

class SchemaParseFailure {
    public final String path;
    public final String reason;
    public final Map<String, Object> data;

    public SchemaParseFailure(String path, String reason, Map<String, Object> data) {
        this.path = path;
        this.reason = reason;
        this.data = data;
    }
}

class Invocation {
    final String functionName;
    final Map<String, Object> functionArgument;
    boolean verified = false;

    public Invocation(String functionName, Map<String, Object> functionArgument) {
        this.functionName = functionName;
        this.functionArgument = functionArgument;
    }
}
