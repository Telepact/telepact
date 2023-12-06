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

class JApiSchemaTuple {
    public final List<Object> original;
    public final Map<String, Type> parsed;

    public JApiSchemaTuple(List<Object> original, Map<String, Type> parsed) {
        this.original = original;
        this.parsed = parsed;
    }
}

class FieldNameAndFieldDeclaration {

    public final String fieldName;
    public final FieldDeclaration fieldDeclaration;

    public FieldNameAndFieldDeclaration(
            String fieldName,
            FieldDeclaration fieldDeclaration) {
        this.fieldName = fieldName;
        this.fieldDeclaration = fieldDeclaration;
    }
}

class FieldDeclaration {

    public final TypeDeclaration typeDeclaration;
    public final boolean optional;

    public FieldDeclaration(
            TypeDeclaration typeDeclaration,
            boolean optional) {
        this.typeDeclaration = typeDeclaration;
        this.optional = optional;
    }
}

class TypeDeclaration {
    public final Type type;
    public final boolean nullable;
    public final List<TypeDeclaration> typeParameters;

    public TypeDeclaration(
            Type type,
            boolean nullable, List<TypeDeclaration> typeParameters) {
        this.type = type;
        this.nullable = nullable;
        this.typeParameters = typeParameters;
    }

    public List<ValidationFailure> validate(Object value, List<TypeDeclaration> generics) {
        if (value == null) {
            var isNullable = this.type instanceof Generic g
                    ? generics.get(g.index).nullable
                    : this.nullable;
            if (!isNullable) {
                return Collections.singletonList(new ValidationFailure("",
                        "NullInvalidForNonNullType"));
            } else {
                return Collections.emptyList();
            }
        } else {
            return this.type.validate(value, this.typeParameters, generics);
        }
    }

    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<TypeDeclaration> generics,
            MockRandom random) {
        if (this.nullable && !useStartingValue && random.nextBoolean()) {
            return null;
        } else {
            return this.type.generateRandomValue(startingValue, useStartingValue, includeRandomOptionalFields,
                    this.typeParameters, generics, random);
        }
    }
}

class TypeDeclarationRoot {
    public final Type type;
    public final boolean nullable;

    public TypeDeclarationRoot(
            Type type,
            boolean nullable) {
        this.type = type;
        this.nullable = nullable;
    }
}

interface Type {
    public int getTypeParameterCount();

    public List<ValidationFailure> validate(Object value, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics);

    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics,
            MockRandom random);
}

class JsonBoolean implements Type {

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics) {
        if (value instanceof Boolean) {
            return Collections.emptyList();
        } else if (value instanceof Number) {
            return Collections.singletonList(
                    new ValidationFailure("", "NumberInvalidForBooleanType"));
        } else if (value instanceof String) {
            return Collections.singletonList(
                    new ValidationFailure("", "StringInvalidForBooleanType"));
        } else if (value instanceof List) {
            return Collections.singletonList(
                    new ValidationFailure("", "ArrayInvalidForBooleanType"));
        } else if (value instanceof Map) {
            return Collections.singletonList(
                    new ValidationFailure("", "ObjectInvalidForBooleanType"));
        } else {
            return Collections.singletonList(
                    new ValidationFailure("", "ValueInvalidForBooleanType"));
        }
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics,
            MockRandom random) {
        if (useStartingValue) {
            return startingValue;
        } else {
            return random.nextBoolean();
        }
    }

}

class JsonInteger implements Type {
    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics) {
        if (value instanceof Boolean) {
            return Collections.singletonList(
                    new ValidationFailure("", "BooleanInvalidForIntegerType"));
        } else if (value instanceof BigInteger bi || value instanceof BigDecimal bd) {
            return Collections.singletonList(
                    new ValidationFailure("", "NumberOutOfRange"));
        } else if (value instanceof Number) {
            if (value instanceof Long || value instanceof Integer) {
                return Collections.emptyList();
            } else {
                return Collections.singletonList(new ValidationFailure("",
                        "NumberInvalidForIntegerType"));
            }
        } else if (value instanceof String) {
            return Collections.singletonList(
                    new ValidationFailure("", "StringInvalidForIntegerType"));
        } else if (value instanceof List) {
            return Collections.singletonList(
                    new ValidationFailure("", "ArrayInvalidForIntegerType"));
        } else if (value instanceof Map) {
            return Collections.singletonList(
                    new ValidationFailure("", "ObjectInvalidForIntegerType"));
        } else {
            return Collections.singletonList(
                    new ValidationFailure("", "ValueInvalidForIntegerType"));
        }
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics,
            MockRandom random) {
        if (useStartingValue) {
            return startingValue;
        } else {
            return random.nextInt();
        }
    }
}

class JsonNumber implements Type {
    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics) {
        if (value instanceof Boolean) {
            return Collections.singletonList(
                    new ValidationFailure("", "BooleanInvalidForNumberType"));
        } else if (value instanceof BigInteger bi || value instanceof BigDecimal bd) {
            return Collections.singletonList(
                    new ValidationFailure("", "NumberOutOfRange"));
        } else if (value instanceof Number) {
            return Collections.emptyList();
        } else if (value instanceof String) {
            return Collections.singletonList(
                    new ValidationFailure("", "StringInvalidForNumberType"));
        } else if (value instanceof List) {
            return Collections.singletonList(
                    new ValidationFailure("", "ArrayInvalidForNumberType"));
        } else if (value instanceof Map) {
            return Collections.singletonList(
                    new ValidationFailure("", "ObjectInvalidForNumberType"));
        } else {
            return Collections.singletonList(
                    new ValidationFailure("", "ValueInvalidForNumberType"));
        }
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics,
            MockRandom random) {
        if (useStartingValue) {
            return startingValue;
        } else {
            return random.nextDouble();
        }
    }
}

class JsonString implements Type {
    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics) {
        if (value instanceof Boolean) {
            return Collections.singletonList(
                    new ValidationFailure("", "BooleanInvalidForStringType"));
        } else if (value instanceof Number) {
            return Collections.singletonList(
                    new ValidationFailure("", "NumberInvalidForStringType"));
        } else if (value instanceof String) {
            return Collections.emptyList();
        } else if (value instanceof List) {
            return Collections.singletonList(
                    new ValidationFailure("", "ArrayInvalidForStringType"));
        } else if (value instanceof Map) {
            return Collections.singletonList(
                    new ValidationFailure("", "ObjectInvalidForStringType"));
        } else {
            return Collections.singletonList(
                    new ValidationFailure("", "ValueInvalidForStringType"));
        }
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics,
            MockRandom random) {
        if (useStartingValue) {
            return startingValue;
        } else {
            return random.nextString();
        }
    }
}

class JsonArray implements Type {

    @Override
    public int getTypeParameterCount() {
        return 1;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics) {
        if (value instanceof Boolean) {
            return Collections.singletonList(
                    new ValidationFailure("", "BooleanInvalidForArrayType"));
        } else if (value instanceof Number) {
            return Collections.singletonList(
                    new ValidationFailure("", "NumberInvalidForArrayType"));
        } else if (value instanceof String) {
            return Collections.singletonList(
                    new ValidationFailure("", "StringInvalidForArrayType"));
        } else if (value instanceof List l) {
            var nestedTypeDeclaration = typeParameters.get(0);
            var validationFailures = new ArrayList<ValidationFailure>();
            for (var i = 0; i < l.size(); i += 1) {
                var element = l.get(i);
                var nestedValidationFailures = nestedTypeDeclaration.validate(element, generics);
                final var index = i;
                var nestedValidationFailuresWithPath = nestedValidationFailures
                        .stream()
                        .map(f -> new ValidationFailure("[%d]%s".formatted(index, f.path), f.reason))
                        .toList();
                validationFailures.addAll(nestedValidationFailuresWithPath);
            }
            return validationFailures;
        } else if (value instanceof Map) {
            return Collections.singletonList(
                    new ValidationFailure("", "ObjectInvalidForArrayType"));
        } else {
            return Collections.singletonList(
                    new ValidationFailure("", "ValueInvalidForArrayType"));
        }
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics,
            MockRandom random) {
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
}

class JsonObject implements Type {

    @Override
    public int getTypeParameterCount() {
        return 1;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics) {
        if (value instanceof Boolean) {
            return Collections.singletonList(
                    new ValidationFailure("", "BooleanInvalidForObjectType"));
        } else if (value instanceof Number) {
            return Collections.singletonList(
                    new ValidationFailure("", "NumberInvalidForObjectType"));
        } else if (value instanceof String) {
            return Collections.singletonList(
                    new ValidationFailure("", "StringInvalidForObjectType"));
        } else if (value instanceof List) {
            return Collections.singletonList(
                    new ValidationFailure("", "ArrayInvalidForObjectType"));
        } else if (value instanceof Map<?, ?> m) {
            var nestedTypeDeclaration = typeParameters.get(0);
            var validationFailures = new ArrayList<ValidationFailure>();
            for (Map.Entry<?, ?> entry : m.entrySet()) {
                var k = (String) entry.getKey();
                var v = entry.getValue();
                var nestedValidationFailures = nestedTypeDeclaration.validate(v, generics);
                var nestedValidationFailuresWithPath = nestedValidationFailures
                        .stream()
                        .map(f -> new ValidationFailure("{%s}%s".formatted(k, f.path), f.reason))
                        .toList();
                validationFailures.addAll(nestedValidationFailuresWithPath);
            }
            return validationFailures;
        } else {
            return Collections.singletonList(
                    new ValidationFailure("", "ValueInvalidForObjectType"));
        }
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics,
            MockRandom random) {
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
}

class JsonAny implements Type {
    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics) {
        return List.of();
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics,
            MockRandom random) {
        var selectType = random.nextInt(3);
        if (selectType == 0) {
            return random.nextBoolean();
        } else if (selectType == 1) {
            return random.nextInt();
        } else {
            return random.nextString();
        }
    }
}

class Generic implements Type {
    public final int index;

    public Generic(int index) {
        this.index = index;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics) {
        var typeDeclaration = generics.get(this.index);
        return typeDeclaration.validate(value, List.of());
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics,
            MockRandom random) {
        var genericTypeDeclaration = generics.get(this.index);
        return genericTypeDeclaration.generateRandomValue(startingValue, useStartingValue,
                includeRandomOptionalFields, List.of(), random);
    }
}

class Struct implements Type {

    public final String name;
    public final Map<String, FieldDeclaration> fields;
    public final int typeParameterCount;

    public Struct(String name, Map<String, FieldDeclaration> fields, int typeParameterCount) {
        this.name = name;
        this.fields = fields;
        this.typeParameterCount = typeParameterCount;
    }

    @Override
    public int getTypeParameterCount() {
        return this.typeParameterCount;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics) {
        if (value instanceof Boolean) {
            return Collections.singletonList(
                    new ValidationFailure("", "BooleanInvalidForStructType"));
        } else if (value instanceof Number) {
            return Collections.singletonList(
                    new ValidationFailure("", "NumberInvalidForStructType"));
        } else if (value instanceof String) {
            return Collections.singletonList(
                    new ValidationFailure("", "StringInvalidForStructType"));
        } else if (value instanceof List) {
            return Collections.singletonList(
                    new ValidationFailure("", "ArrayInvalidForStructType"));
        } else if (value instanceof Map<?, ?> m) {
            return validateStructFields(this.fields, (Map<String, Object>) m, typeParameters);
        } else {
            return Collections.singletonList(
                    new ValidationFailure("", "ValueInvalidForStructType"));
        }
    }

    public static List<ValidationFailure> validateStructFields(
            Map<String, FieldDeclaration> fields,
            Map<String, Object> actualStruct, List<TypeDeclaration> typeParameters) {
        var validationFailures = new ArrayList<ValidationFailure>();

        var missingFields = new ArrayList<String>();
        for (Map.Entry<String, FieldDeclaration> entry : fields.entrySet()) {
            var fieldName = entry.getKey();
            var fieldDeclaration = entry.getValue();
            if (!actualStruct.containsKey(fieldName) && !fieldDeclaration.optional) {
                missingFields.add(fieldName);
            }
        }

        for (var missingField : missingFields) {
            var validationFailure = new ValidationFailure(".%s".formatted(missingField),
                    "RequiredStructFieldMissing");
            validationFailures
                    .add(validationFailure);
        }

        for (Map.Entry<String, Object> entry : actualStruct.entrySet()) {
            var fieldName = entry.getKey();
            var fieldValue = entry.getValue();
            var referenceField = fields.get(fieldName);
            if (referenceField == null) {
                var validationFailure = new ValidationFailure(".%s".formatted(fieldName),
                        "UnknownStructField");
                validationFailures
                        .add(validationFailure);
                continue;
            }
            var nestedValidationFailures = referenceField.typeDeclaration.validate(fieldValue, typeParameters);
            var nestedValidationFailuresWithPath = nestedValidationFailures
                    .stream()
                    .map(f -> new ValidationFailure(".%s%s".formatted(fieldName, f.path), f.reason))
                    .toList();
            validationFailures.addAll(nestedValidationFailuresWithPath);
        }

        return validationFailures;
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics,
            MockRandom random) {
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
            Map<String, FieldDeclaration> referenceStruct, Map<String, Object> startingStruct,
            boolean includeRandomOptionalFields, List<TypeDeclaration> typeParameters,
            MockRandom random) {

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
}

class Enum implements Type {

    public final String name;
    public final Map<String, Struct> values;
    public final int typeParameterCount;

    public Enum(String name, Map<String, Struct> values, int typeParameterCount) {
        this.name = name;
        this.values = values;
        this.typeParameterCount = typeParameterCount;
    }

    @Override
    public int getTypeParameterCount() {
        return this.typeParameterCount;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics) {
        if (value instanceof Boolean) {
            return Collections.singletonList(
                    new ValidationFailure("", "BooleanInvalidForEnumType"));
        } else if (value instanceof Number) {
            return Collections.singletonList(
                    new ValidationFailure("", "NumberInvalidForEnumType"));
        } else if (value instanceof String) {
            return Collections.singletonList(
                    new ValidationFailure("", "StringInvalidForEnumType"));
        } else if (value instanceof List) {
            return Collections.singletonList(
                    new ValidationFailure("", "ArrayInvalidForEnumType"));
        } else if (value instanceof Map<?, ?> m) {
            return validateEnumValues(this.values, m, typeParameters);
        } else {
            return Collections.singletonList(
                    new ValidationFailure("", "ValueInvalidForEnumType"));
        }
    }

    private List<ValidationFailure> validateEnumValues(
            Map<String, Struct> referenceValues,
            Map<?, ?> actual, List<TypeDeclaration> typeParameters) {
        if (actual.size() != 1) {
            return Collections.singletonList(
                    new ValidationFailure("",
                            "EnumDoesNotHaveExactlyOneField"));
        }
        var entry = actual.entrySet().stream().findFirst().get();
        var enumTarget = (String) entry.getKey();
        var enumPayload = entry.getValue();

        var referenceStruct = referenceValues.get(enumTarget);
        if (referenceStruct == null) {
            return Collections
                    .singletonList(new ValidationFailure(".%s".formatted(enumTarget),
                            "UnknownEnumField"));
        }

        if (enumPayload instanceof Boolean) {
            return Collections.singletonList(new ValidationFailure(".%s".formatted(enumTarget),
                    "BooleanInvalidForEnumStructType"));
        } else if (enumPayload instanceof Number) {
            return Collections.singletonList(new ValidationFailure(".%s".formatted(enumTarget),
                    "NumberInvalidForEnumStructType"));
        } else if (enumPayload instanceof String) {
            return Collections.singletonList(new ValidationFailure(".%s".formatted(enumTarget),
                    "StringInvalidForEnumStructType"));
        } else if (enumPayload instanceof List) {
            return Collections.singletonList(new ValidationFailure(".%s".formatted(enumTarget),
                    "ArrayInvalidForEnumStructType"));
        } else if (enumPayload instanceof Map<?, ?> m2) {
            var nestedValidationFailures = validateEnumStruct(referenceStruct, enumTarget,
                    (Map<String, Object>) m2, typeParameters);
            var nestedValidationFailuresWithPath = nestedValidationFailures
                    .stream()
                    .map(f -> new ValidationFailure(".%s%s".formatted(enumTarget, f.path), f.reason))
                    .toList();
            return nestedValidationFailuresWithPath;
        } else {
            return Collections.singletonList(new ValidationFailure(".%s".formatted(enumTarget),
                    "ValueInvalidForEnumStructType"));
        }
    }

    private static List<ValidationFailure> validateEnumStruct(
            Struct enumStruct,
            String enumCase,
            Map<String, Object> actual, List<TypeDeclaration> typeParameters) {
        var validationFailures = new ArrayList<ValidationFailure>();

        var nestedValidationFailures = Struct.validateStructFields(enumStruct.fields,
                actual, typeParameters);
        validationFailures.addAll(nestedValidationFailures);

        return validationFailures;
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics,
            MockRandom random) {
        if (useStartingValue) {
            var startingEnumValue = (Map<String, Object>) startingValue;
            return constructRandomEnum(this.values, startingEnumValue, includeRandomOptionalFields,
                    typeParameters, random);
        } else {
            return constructRandomEnum(this.values, new HashMap<>(), includeRandomOptionalFields,
                    typeParameters, random);
        }
    }

    private static Map<String, Object> constructRandomEnum(Map<String, Struct> enumValuesReference,
            Map<String, Object> startingEnum,
            boolean includeRandomOptionalFields,
            List<TypeDeclaration> typeParameters,
            MockRandom random) {
        var existingEnumValue = startingEnum.keySet().stream().findAny();
        if (existingEnumValue.isPresent()) {
            var enumValue = existingEnumValue.get();
            var enumStructType = enumValuesReference.get(enumValue);
            var enumStartingStruct = (Map<String, Object>) startingEnum.get(enumValue);

            return Map.of(enumValue, Struct.constructRandomStruct(enumStructType.fields, enumStartingStruct,
                    includeRandomOptionalFields, typeParameters, random));
        } else {
            var sortedEnumValuesReference = new ArrayList<>(enumValuesReference.entrySet());
            Collections.sort(sortedEnumValuesReference, (e1, e2) -> e1.getKey().compareTo(e2.getKey()));

            var randomIndex = random.nextInt(sortedEnumValuesReference.size());
            var enumEntry = sortedEnumValuesReference.get(randomIndex);

            var enumValue = enumEntry.getKey();
            var enumData = enumEntry.getValue();

            return Map.of(enumValue,
                    Struct.constructRandomStruct(enumData.fields, new HashMap<>(), includeRandomOptionalFields,
                            typeParameters, random));
        }

    }
}

class Fn implements Type {

    public final String name;
    public final Struct arg;
    public final Enum result;

    public Fn(String name, Struct input, Enum output) {
        this.name = name;
        this.arg = input;
        this.result = output;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics) {
        return this.arg.validate(value, typeParameters, generics);
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics,
            MockRandom random) {
        if (useStartingValue) {
            var startingFnValue = (Map<String, Object>) startingValue;
            return Struct.constructRandomStruct(this.arg.fields, startingFnValue, includeRandomOptionalFields,
                    List.of(),
                    random);
        } else {
            return Struct.constructRandomStruct(this.arg.fields, new HashMap<>(), includeRandomOptionalFields,
                    List.of(),
                    random);
        }
    }
}

// TODO: trait is not a type
class Trait implements Type {
    public final String name;
    public final Fn fn;
    public final String regex;

    public Trait(String name, Fn fn, String regex) {
        this.name = name;
        this.fn = fn;
        this.regex = regex;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'validate'");
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<TypeDeclaration> typeParameters, List<TypeDeclaration> generics,
            MockRandom random) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'generateRandomValue'");
    }
}

// TODO: info is not a type
class Info implements Type {
    public final String name;

    public Info(String name) {
        this.name = name;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'validate'");
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<TypeDeclaration> typeParameters, List<TypeDeclaration> generics,
            MockRandom random) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'generateRandomValue'");
    }
}

class Ext implements Type {
    public final String name;
    public final TypeExtension typeExtension;
    public final int typeParameterCount;

    public Ext(String name, TypeExtension typeExtension, int typeParameterCount) {
        this.name = name;
        this.typeExtension = typeExtension;
        this.typeParameterCount = typeParameterCount;
    }

    @Override
    public int getTypeParameterCount() {
        return this.typeParameterCount;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<TypeDeclaration> typeParameters,
            List<TypeDeclaration> generics) {
        return this.typeExtension.validate(value);
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<TypeDeclaration> typeParameters, List<TypeDeclaration> generics,
            MockRandom random) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'generateRandomValue'");
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
    public final String path;
    public final String reason;

    public ValidationFailure(String path, String reason) {
        this.path = path;
        this.reason = reason;
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
