package io.github.brenbar.japi;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.regex.Pattern;

class _UApiSchemaUtil {

    static UApiSchemaTuple combineUApiSchemas(JApiSchema first, JApiSchema second) {
        List<Object> firstOriginal = first.original;
        List<Object> secondOriginal = second.original;
        Map<String, UType> firstParsed = first.parsed;
        Map<String, UType> secondParsed = second.parsed;

        // Check for duplicates
        var duplicatedSchemaKeys = new HashSet<String>();
        for (var key : firstParsed.keySet()) {
            if (secondParsed.containsKey(key)) {
                duplicatedSchemaKeys.add(key);
            }
        }
        if (!duplicatedSchemaKeys.isEmpty()) {
            var sortedKeys = new TreeSet<String>(duplicatedSchemaKeys);
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure("",
                    "DuplicateSchemaKeys", Map.of("keys", sortedKeys))));
        }

        var original = new ArrayList<Object>();
        original.addAll(firstOriginal);
        original.addAll(secondOriginal);

        var schemaKeysToIndex = new HashMap<String, Integer>();
        var index = 0;
        for (var definition : original) {
            Map<String, Object> def = (Map<String, Object>) definition;

            String schemaKey = findSchemaKey(def, index);

            schemaKeysToIndex.put(schemaKey, index);
            index += 1;
        }

        // Any traits in the first schema need to be applied to the second
        for (var e : firstParsed.entrySet()) {
            if (e.getValue() instanceof UTrait t) {
                applyTraitToParsedTypes(t, secondParsed, schemaKeysToIndex);
            }
        }

        // And vice versa
        for (var e : secondParsed.entrySet()) {
            if (e.getValue() instanceof UTrait t) {
                applyTraitToParsedTypes(t, firstParsed, schemaKeysToIndex);
            }
        }

        var parsed = new HashMap<String, UType>();
        parsed.putAll(firstParsed);
        parsed.putAll(secondParsed);

        return new UApiSchemaTuple(original, parsed);
    }

    static UApiSchemaTuple parseUApiSchema(String uApiSchemaJson, Map<String, TypeExtension> typeExtensions) {
        var parsedTypes = new HashMap<String, UType>();
        var parseFailures = new ArrayList<SchemaParseFailure>();

        var objectMapper = new ObjectMapper();
        List<Object> originalUApiSchema;
        try {
            originalUApiSchema = objectMapper.readValue(uApiSchemaJson, new TypeReference<>() {
            });
        } catch (IOException e) {
            throw new JApiSchemaParseError(
                    List.of(new SchemaParseFailure("(document-root)", "ArrayTypeRequired", Map.of())),
                    e);
        }

        var schemaKeysToIndex = new HashMap<String, Integer>();

        var schemaKeys = new HashSet<String>();
        var duplicateKeys = new HashSet<String>();
        var index = 0;
        for (var definition : originalUApiSchema) {
            Map<String, Object> def;
            try {
                def = (Map<String, Object>) definition;
            } catch (ClassCastException e) {
                parseFailures
                        .add(new SchemaParseFailure("[%d]".formatted(index), "DefinitionMustBeAnObject", Map.of()));
                continue;
            }

            String schemaKey;
            try {
                schemaKey = findSchemaKey(def, index);
            } catch (JApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
                continue;
            }

            if (schemaKeys.contains(schemaKey)) {
                duplicateKeys.add(schemaKey);
            }
            schemaKeys.add(schemaKey);
            schemaKeysToIndex.put(schemaKey, index);
            index += 1;
        }

        if (!duplicateKeys.isEmpty()) {
            parseFailures.add(new SchemaParseFailure("", "DuplicateSchemaKeys", Map.of("keys", duplicateKeys)));
        }

        var traits = new ArrayList<UTrait>();

        var rootTypeParameterCount = 0;
        boolean allowTraitsAndInfo = true;
        for (var schemaKey : schemaKeys) {
            var thisIndex = schemaKeysToIndex.get(schemaKey);
            var thisPath = "[%d]".formatted(index);
            var typ = getOrParseType(thisPath, schemaKey, rootTypeParameterCount, allowTraitsAndInfo,
                    originalUApiSchema,
                    schemaKeysToIndex,
                    parsedTypes, typeExtensions);
            if (typ instanceof UTrait t) {
                traits.add(t);
            }
        }

        for (var trait : traits) {
            try {
                applyTraitToParsedTypes(trait, parsedTypes, schemaKeysToIndex);
            } catch (JApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        // Ensure all type extensions are defined
        for (var entry : typeExtensions.entrySet()) {
            var typeExtensionName = entry.getKey();
            var typeExtension = (UExt) parsedTypes.get(typeExtensionName);
            if (typeExtension == null) {
                parseFailures
                        .add(new SchemaParseFailure("", "UndefinedTypeExtension", Map.of("name", typeExtensionName)));
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new JApiSchemaParseError(parseFailures);
        }

        return new UApiSchemaTuple(originalUApiSchema, parsedTypes);
    }

    private static String findSchemaKey(Map<String, Object> definition, int index) {
        var regex = "^((fn|trait|info)|((struct|enum|ext)(<[0-2]>)?))\\..*";
        for (var e : definition.keySet()) {
            if (e.matches(regex)) {
                return e;
            }
        }
        var sortedKeys = new TreeSet<>(definition.keySet());
        Map<String, Object> sortedMap = new TreeMap<>(Map.of("regex", regex, "keys", sortedKeys));
        throw new JApiSchemaParseError(List.of(new SchemaParseFailure("[%d]".formatted(index),
                "DefinitionObjectMustHaveOneKeyMatchingRegex", sortedMap)));
    }

    static void applyTraitToParsedTypes(UTrait trait, Map<String, UType> parsedTypes,
            Map<String, Integer> schemaKeysToIndex) {
        var parseFailures = new ArrayList<SchemaParseFailure>();
        for (var parsedType : parsedTypes.entrySet()) {
            UFn f;
            try {
                f = (UFn) parsedType.getValue();
            } catch (ClassCastException e) {
                continue;
            }

            String traitRegex = trait.regex;
            String fnName = f.name;

            var regex = Pattern.compile(traitRegex);
            var matcher = regex.matcher(fnName);
            if (!matcher.find()) {
                continue;
            }

            String traitName = trait.name;
            UStruct fnArg = f.arg;
            Map<String, UFieldDeclaration> fnArgFields = fnArg.fields;
            UEnum fnResult = f.result;
            Map<String, UStruct> fnResultValues = fnResult.values;
            UFn traitFn = trait.fn;
            String traitFnName = traitFn.name;
            UStruct traitFnArg = traitFn.arg;
            Map<String, UFieldDeclaration> traitFnArgFields = traitFnArg.fields;
            UEnum traitFnResult = traitFn.result;
            Map<String, UStruct> traitFnResultValues = traitFnResult.values;

            if (fnName.startsWith("fn._")) {
                // Only internal traits can change internal functions
                if (!traitName.startsWith("trait._")) {
                    continue;
                }
            }

            for (var traitArgumentField : traitFnArgFields.entrySet()) {
                var newKey = traitArgumentField.getKey();
                if (fnArgFields.containsKey(newKey)) {
                    var index = schemaKeysToIndex.get(traitName);
                    parseFailures.add(new SchemaParseFailure("[%d].%s.%s".formatted(index, traitFnName, newKey),
                            "TraitArgumentFieldAlreadyInUseByFunction", Map.of("fn", fnName)));
                }
                fnArgFields.put(newKey, traitArgumentField.getValue());
            }

            for (var traitResultField : traitFnResultValues.entrySet()) {
                var newKey = traitResultField.getKey();
                if (fnResultValues.containsKey(newKey)) {
                    var index = schemaKeysToIndex.get(traitName);
                    parseFailures.add(new SchemaParseFailure("[%d].->.%s".formatted(index, newKey),
                            "TraitResultValueAlreadyInUseByFunction", Map.of("fn", fnName)));
                }
                fnResultValues.put(newKey, traitResultField.getValue());
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new JApiSchemaParseError(parseFailures);
        }
    }

    public static UTrait parseTraitType(
            Map<String, Object> traitDefinitionAsParsedJson,
            String schemaKey,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes,
            Map<String, TypeExtension> typeExtensions) {
        Map<String, Object> def;
        try {
            def = (Map<String, Object>) traitDefinitionAsParsedJson.get(schemaKey);
        } catch (ClassCastException e) {
            var index = schemaKeysToIndex.get(schemaKey);
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure("[%d].%s".formatted(index, schemaKey),
                    "ObjectTypeRequired", Map.of())));
        }

        String traitFunctionRegex;
        String traitFunctionKey;
        if (def.containsKey("fn.*")) {
            traitFunctionKey = "fn.*";
            traitFunctionRegex = "^fn\\.[a-zA-Z]";
        } else if (def.containsKey("fn._?*")) {
            if (!schemaKey.startsWith("trait._")) {
                var index = schemaKeysToIndex.get(schemaKey);
                throw new JApiSchemaParseError(List.of(new SchemaParseFailure("[%d].%s".formatted(index, schemaKey),
                        "TraitDefinitionCannotTargetInternalFunctions", Map.of())));
            }
            traitFunctionKey = "fn._?*";
            traitFunctionRegex = "^fn\\.[a-zA-Z_]";
        } else {
            var index = schemaKeysToIndex.get(schemaKey);
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure("[%d].%s".formatted(index, schemaKey),
                    "InvalidFunctionTarget", Map.of())));
        }

        var traitFunction = parseFunctionType(def, traitFunctionKey, originalJApiSchema, schemaKeysToIndex, parsedTypes,
                typeExtensions,
                true);

        return new UTrait(schemaKey, traitFunction, traitFunctionRegex);
    }

    private static UFn parseFunctionType(
            Map<String, Object> functionDefinitionAsParsedJson,
            String schemaKey,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes,
            Map<String, TypeExtension> typeExtensions,
            boolean isForTrait) {
        Map<String, Object> argumentDefinitionAsParsedJson;
        try {
            argumentDefinitionAsParsedJson = (Map<String, Object>) functionDefinitionAsParsedJson.get(schemaKey);
        } catch (ClassCastException e) {
            var index = schemaKeysToIndex.get(schemaKey);
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure("[%d].%s".formatted(index, schemaKey),
                    "ObjectTypeRequired", Map.of())));
        }
        var argumentFields = new HashMap<String, UFieldDeclaration>();
        var isForEnum = false;
        var typeParameterCount = 0;
        for (var entry : argumentDefinitionAsParsedJson.entrySet()) {
            var fieldDeclaration = entry.getKey();
            var typeDeclarationValue = entry.getValue();
            var parsedField = parseField(schemaKey, fieldDeclaration,
                    typeDeclarationValue, isForEnum, typeParameterCount, originalJApiSchema, schemaKeysToIndex,
                    parsedTypes,
                    typeExtensions);
            argumentFields.put(parsedField.fieldName, parsedField.fieldDeclaration);
        }

        var argType = new UStruct(schemaKey, argumentFields, typeParameterCount);

        Map<String, Object> resultDefinitionAsParsedJson;
        try {
            resultDefinitionAsParsedJson = (Map<String, Object>) functionDefinitionAsParsedJson.get("->");
        } catch (ClassCastException e) {
            var index = schemaKeysToIndex.get(schemaKey);
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure("[%d].->".formatted(index),
                    "ObjectTypeRequired", Map.of())));
        }

        if (!isForTrait) {
            if (!resultDefinitionAsParsedJson.containsKey("ok")) {
                var index = schemaKeysToIndex.get(schemaKey);
                throw new JApiSchemaParseError(List.of(new SchemaParseFailure("[%d].->.ok".formatted(index),
                        "RequiredKeyMissing", Map.of())));
            }
        }

        var parseFailures = new ArrayList<SchemaParseFailure>();

        var values = new HashMap<String, UStruct>();
        for (var entry : resultDefinitionAsParsedJson.entrySet()) {
            Map<String, Object> enumValueData;
            try {
                enumValueData = (Map<String, Object>) entry.getValue();
            } catch (ClassCastException e) {
                var enumValue = entry.getKey();
                var index = schemaKeysToIndex.get(schemaKey);
                parseFailures.add(new SchemaParseFailure("[%d].->.%s".formatted(index, enumValue),
                        "ObjectTypeRequired", Map.of()));
                continue;
            }
            var enumValue = entry.getKey();

            var fields = new HashMap<String, UFieldDeclaration>();
            for (var structEntry : enumValueData.entrySet()) {
                var fieldDeclaration = structEntry.getKey();
                var typeDeclarationValue = structEntry.getValue();
                var parsedField = parseField(schemaKey, fieldDeclaration,
                        typeDeclarationValue, isForEnum, typeParameterCount, originalJApiSchema, schemaKeysToIndex,
                        parsedTypes,
                        typeExtensions);
                fields.put(parsedField.fieldName, parsedField.fieldDeclaration);
            }

            var enumStruct = new UStruct("->.%s".formatted(enumValue), fields, typeParameterCount);

            values.put(enumValue, enumStruct);
        }

        if (!parseFailures.isEmpty()) {
            throw new JApiSchemaParseError(parseFailures);
        }

        var resultType = new UEnum("%s.->".formatted(schemaKey), values, typeParameterCount);

        var type = new UFn(schemaKey, argType, resultType);

        return type;
    }

    private static UStruct parseStructType(
            Map<String, Object> structDefinitionAsParsedJson,
            String schemaKey,
            int typeParameterCount,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes,
            Map<String, TypeExtension> typeExtensions) {
        var definition = (Map<String, Object>) structDefinitionAsParsedJson.get(schemaKey);

        var fields = new HashMap<String, UFieldDeclaration>();
        for (var entry : definition.entrySet()) {
            var fieldDeclaration = entry.getKey();
            var typeDeclarationValue = entry.getValue();
            var parsedField = parseField(schemaKey, fieldDeclaration,
                    typeDeclarationValue, false, typeParameterCount, originalJApiSchema, schemaKeysToIndex, parsedTypes,
                    typeExtensions);
            fields.put(parsedField.fieldName, parsedField.fieldDeclaration);
        }

        var type = new UStruct(schemaKey, fields, typeParameterCount);

        return type;
    }

    private static UEnum parseEnumType(
            Map<String, Object> enumDefinitionAsParsedJson,
            String schemaKey,
            int typeParameterCount,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes,
            Map<String, TypeExtension> typeExtensions) {
        var index = schemaKeysToIndex.get(schemaKey);

        var definition = (Map<String, Object>) enumDefinitionAsParsedJson.get(schemaKey);

        var parseFailures = new ArrayList<SchemaParseFailure>();

        var values = new HashMap<String, UStruct>();
        for (var entry : definition.entrySet()) {
            Map<String, Object> enumStructData;
            try {
                enumStructData = (Map<String, Object>) entry.getValue();
            } catch (ClassCastException e) {
                var enumValue = entry.getKey();
                parseFailures.add(
                        new SchemaParseFailure("[%d].->.%s".formatted(index, enumValue),
                                "ObjectTypeRequired", Map.of()));
                continue;
            }
            var enumValue = entry.getKey();

            var regex = Pattern.compile("^([a-zA-Z_]+[a-zA-Z0-9_]*)$");
            var matcher = regex.matcher(enumValue);
            if (!matcher.find()) {
                parseFailures.add(new SchemaParseFailure("[%d].->".formatted(index),
                        "InvalidEnumValue", Map.of("value", enumValue)));
                continue;
            }

            var fields = new HashMap<String, UFieldDeclaration>();
            for (var structEntry : enumStructData.entrySet()) {
                var fieldDeclaration = structEntry.getKey();
                var typeDeclarationValue = structEntry.getValue();
                UFieldNameAndFieldDeclaration parsedField;
                try {
                    parsedField = parseField("[%d].->.%s".formatted(index, enumValue), fieldDeclaration,
                            typeDeclarationValue, false, typeParameterCount, originalJApiSchema, schemaKeysToIndex,
                            parsedTypes,
                            typeExtensions);
                } catch (JApiSchemaParseError e) {
                    parseFailures.addAll(e.schemaParseFailures);
                    continue;
                }
                String fieldName = parsedField.fieldName;
                UFieldDeclaration fieldDeclarationInst = parsedField.fieldDeclaration;
                fields.put(fieldName, fieldDeclarationInst);
            }

            var enumStruct = new UStruct("%s.%s".formatted(schemaKey, enumValue), fields, typeParameterCount);

            values.put(enumValue, enumStruct);
        }

        if (!parseFailures.isEmpty()) {
            throw new JApiSchemaParseError(parseFailures);
        }

        var type = new UEnum(schemaKey, values, typeParameterCount);

        return type;
    }

    private static UFieldNameAndFieldDeclaration parseField(
            String path,
            String fieldDeclaration,
            Object typeDeclarationValue,
            boolean isForEnum,
            int typeParameterCount,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes,
            Map<String, TypeExtension> typeExtensions) {
        var regex = Pattern.compile("^([a-zA-Z_]+[a-zA-Z0-9_]*)(!)?$");
        var matcher = regex.matcher(fieldDeclaration);
        if (!matcher.find()) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "InvalidFieldKey", Map.of("field", fieldDeclaration))));
        }

        String fieldName = matcher.group(1);

        boolean optional = matcher.group(2) != null;

        List<Object> typeDeclarationArray;
        try {
            typeDeclarationArray = (List<Object>) typeDeclarationValue;
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "ArrayTypeRequired", Map.of())));
        }

        if (optional && isForEnum) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "EnumKeysCannotBeMarkedAsOptional", Map.of())));
        }

        var typeDeclaration = parseTypeDeclaration(path, typeDeclarationArray, typeParameterCount, originalJApiSchema,
                schemaKeysToIndex,
                parsedTypes,
                typeExtensions);

        return new UFieldNameAndFieldDeclaration(fieldName, new UFieldDeclaration(typeDeclaration, optional));
    }

    private static UTypeDeclaration parseTypeDeclaration(String path, List<Object> typeDeclarationArray,
            int thisTypeParameterCount,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes, Map<String, TypeExtension> typeExtensions) {
        if (typeDeclarationArray.size() == 0) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "ArrayMustNotBeEmpty", Map.of())));
        }

        var thisPath = "%s[%d]".formatted(path, 0);

        String rootTypeString;
        try {
            rootTypeString = (String) typeDeclarationArray.get(0);
        } catch (ClassCastException ex) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(thisPath,
                    "StringTypeRequired", Map.of())));
        }

        var regex = Pattern.compile("^(.*?)(\\?)?$");
        var matcher = regex.matcher(rootTypeString);
        if (!matcher.find()) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(thisPath,
                    "CouldNotParseType", Map.of())));
        }

        var typeName = matcher.group(1);
        var nullable = matcher.group(2) != null;

        boolean allowTraitsAndInfo = false;
        var type = getOrParseType(thisPath, typeName, thisTypeParameterCount, allowTraitsAndInfo, originalJApiSchema,
                schemaKeysToIndex, parsedTypes,
                typeExtensions);

        if (type instanceof UGeneric && nullable) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(thisPath,
                    "CannotMarkGenericAsNullable", Map.of())));
        }

        var givenTypeParameterCount = typeDeclarationArray.size() - 1;
        if (type.getTypeParameterCount() != givenTypeParameterCount) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "IncorrectNumberOfTypeParameters", Map.of())));
        }

        var parseFailures = new ArrayList<SchemaParseFailure>();
        var typeParameters = new ArrayList<UTypeDeclaration>();
        var givenTypeParameters = typeDeclarationArray.subList(1, typeDeclarationArray.size());
        var index = 0;
        for (var e : givenTypeParameters) {
            var loopPath = "%s[%d]".formatted(path, index);
            index += 1;
            List<Object> l;
            try {
                l = (List<Object>) e;
            } catch (ClassCastException ex) {
                parseFailures.add(new SchemaParseFailure("%s[%d]".formatted(path, index),
                        "ArrayTypeRequired", Map.of()));
                continue;
            }

            UTypeDeclaration typeParameterTypeDeclaration;
            try {
                typeParameterTypeDeclaration = parseTypeDeclaration(loopPath, l, thisTypeParameterCount,
                        originalJApiSchema,
                        schemaKeysToIndex, parsedTypes, typeExtensions);
            } catch (JApiSchemaParseError e2) {
                parseFailures.addAll(e2.schemaParseFailures);
                continue;
            }

            typeParameters.add(typeParameterTypeDeclaration);
        }

        return new UTypeDeclaration(type, nullable, typeParameters);
    }

    private static UType getOrParseType(String path, String typeName, int thisTypeParameterCount,
            boolean allowTraitsAndInfo,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes, Map<String, TypeExtension> typeExtensions) {
        var existingType = parsedTypes.get(typeName);
        if (existingType != null) {
            return existingType;
        }

        var regex = Pattern.compile(
                "^(boolean|integer|number|string|any|array|object|T.([0-2]))|((trait|info|fn|(enum|struct|ext)(<([1-3])>)?)\\.([a-zA-Z_]\\w*))$");
        var matcher = regex.matcher(typeName);
        if (!matcher.find()) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "InvalidType", Map.of("type", typeName))));
        }

        var standardTypeName = matcher.group(1);
        if (standardTypeName != null) {
            return switch (standardTypeName) {
                case "boolean" -> new UBoolean();
                case "integer" -> new UInteger();
                case "number" -> new UNumber();
                case "string" -> new UString();
                case "array" -> new UArray();
                case "object" -> new UObject();
                case "any" -> new UAny();
                default -> {
                    var genericParameterIndexString = matcher.group(2);
                    if (genericParameterIndexString != null) {
                        var genericParameterIndex = Integer.parseInt(genericParameterIndexString);
                        if (genericParameterIndex >= thisTypeParameterCount) {
                            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                                    "MaximumTypeParametersExceeded", Map.of())));
                        }
                        yield new UGeneric(genericParameterIndex);
                    } else {
                        throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                                "InvalidGenericType", Map.of("type", standardTypeName))));
                    }
                }
            };
        }

        var customTypeName = matcher.group(3);
        if (customTypeName != null) {
            var index = schemaKeysToIndex.get(customTypeName);
            if (index == null) {
                throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                        "UndefinedType", Map.of("type", customTypeName))));
            }
            var definition = (Map<String, Object>) originalJApiSchema.get(index);

            var typeParameterCountString = matcher.group(7);
            int typeParameterCount = 0;
            if (typeParameterCountString != null) {
                typeParameterCount = Integer.parseInt(typeParameterCountString);
            }

            UType type;
            if (customTypeName.startsWith("struct")) {
                type = parseStructType(definition, customTypeName, typeParameterCount, originalJApiSchema,
                        schemaKeysToIndex, parsedTypes,
                        typeExtensions);
            } else if (customTypeName.startsWith("enum")) {
                type = parseEnumType(definition, customTypeName, typeParameterCount, originalJApiSchema,
                        schemaKeysToIndex, parsedTypes,
                        typeExtensions);
            } else if (customTypeName.startsWith("fn")) {
                type = parseFunctionType(definition, customTypeName, originalJApiSchema, schemaKeysToIndex, parsedTypes,
                        typeExtensions, false);
            } else if (allowTraitsAndInfo && customTypeName.startsWith("trait")) {
                type = parseTraitType(definition, customTypeName, originalJApiSchema, schemaKeysToIndex, parsedTypes,
                        typeExtensions);
            } else if (allowTraitsAndInfo && customTypeName.startsWith("info")) {
                type = new UInfo(customTypeName);
            } else if (customTypeName.startsWith("ext")) {
                var typeExtension = typeExtensions.get(customTypeName);
                if (typeExtension == null) {
                    throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                            "TypeExtensionImplementationMissing", Map.of("type", customTypeName))));
                }
                type = new UExt(customTypeName, typeExtension, typeParameterCount);
            } else {
                throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                        "InvalidType", Map.of("type", customTypeName))));
            }

            parsedTypes.put(customTypeName, type);

            return type;
        }

        throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                "InvalidType", Map.of("type", typeName))));
    }
}
