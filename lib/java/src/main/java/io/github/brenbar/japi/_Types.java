package io.github.brenbar.japi;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
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
            if (!this.nullable) {
                return Collections.singletonList(new ValidationFailure("",
                        "NullInvalidForNonNullType"));
            } else {
                return Collections.emptyList();
            }
        } else {
            return this.type.validate(value, this.typeParameters, generics);
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
            var validationFailure = new ValidationFailure(missingField,
                    "RequiredStructFieldMissing");
            validationFailures
                    .add(validationFailure);
        }

        for (Map.Entry<String, Object> entry : actualStruct.entrySet()) {
            var fieldName = entry.getKey();
            var fieldValue = entry.getValue();
            var referenceField = fields.get(fieldName);
            if (referenceField == null) {
                var validationFailure = new ValidationFailure(fieldName,
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
                    .singletonList(new ValidationFailure(enumTarget,
                            "UnknownEnumField"));
        }

        if (enumPayload instanceof Boolean) {
            return Collections.singletonList(new ValidationFailure(enumTarget,
                    "BooleanInvalidForEnumStructType"));
        } else if (enumPayload instanceof Number) {
            return Collections.singletonList(new ValidationFailure(enumTarget,
                    "NumberInvalidForEnumStructType"));
        } else if (enumPayload instanceof String) {
            return Collections.singletonList(new ValidationFailure(enumTarget,
                    "StringInvalidForEnumStructType"));
        } else if (enumPayload instanceof List) {
            return Collections.singletonList(new ValidationFailure(enumTarget,
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
            return Collections.singletonList(new ValidationFailure(enumTarget,
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
