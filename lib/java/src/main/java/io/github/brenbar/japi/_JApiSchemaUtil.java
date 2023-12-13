package io.github.brenbar.japi;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.TreeSet;
import java.util.regex.Pattern;

class _JApiSchemaUtil {

    static UApiSchemaTuple combineJApiSchemas(JApiSchema first, JApiSchema second) {
        List<Object> firstOriginal = first.original;
        List<Object> secondOriginal = second.original;
        Map<String, UType> firstParsed = first.parsed;
        Map<String, UType> secondParsed = second.parsed;

        // Any traits in the first schema need to be applied to the second
        for (var e : firstParsed.entrySet()) {
            if (e.getValue() instanceof UTrait t) {
                if (secondParsed.containsKey(t.name)) {
                    throw new JApiSchemaParseError(
                            "Could not combine schemas due to duplicate trait %s".formatted(t.name));
                }
                _JApiSchemaUtil.applyTraitToParsedTypes(t, secondParsed);
            }
        }

        // And vice versa
        for (var e : secondParsed.entrySet()) {
            if (e.getValue() instanceof UTrait t) {
                if (firstParsed.containsKey(t.name)) {
                    throw new JApiSchemaParseError(
                            "Could not combine schemas due to duplicate trait %s".formatted(t.name));
                }
                _JApiSchemaUtil.applyTraitToParsedTypes(t, firstParsed);
            }
        }

        // Check for duplicates
        var duplicatedJsonSchemaKeys = new HashSet<String>();
        for (var key : firstParsed.keySet()) {
            if (secondParsed.containsKey(key)) {
                duplicatedJsonSchemaKeys.add(key);
            }
        }
        if (!duplicatedJsonSchemaKeys.isEmpty()) {
            var sortedKeys = new TreeSet<String>(duplicatedJsonSchemaKeys);
            throw new JApiSchemaParseError(
                    "Final schema has duplicate keys: %s".formatted(sortedKeys));
        }

        var original = new ArrayList<Object>();
        original.addAll(firstOriginal);
        original.addAll(secondOriginal);

        var parsed = new HashMap<String, UType>();
        parsed.putAll(firstParsed);
        parsed.putAll(secondParsed);

        return new UApiSchemaTuple(original, parsed);
    }

    static UApiSchemaTuple parseJApiSchema(String jApiSchemaAsJson, Map<String, TypeExtension> typeExtensions) {
        var parsedTypes = new HashMap<String, UType>();

        var objectMapper = new ObjectMapper();
        List<Object> originalJApiSchema;
        try {
            originalJApiSchema = objectMapper.readValue(jApiSchemaAsJson, new TypeReference<>() {
            });
        } catch (IOException e) {
            throw new JApiSchemaParseError("Document root must be an array of objects", e);
        }

        var schemaKeysToIndex = new HashMap<String, Integer>();

        var schemaKeys = new HashSet<String>();
        var duplicateKeys = new HashSet<String>();
        var index = 0;
        for (var definition : originalJApiSchema) {
            Map<String, Object> def;
            try {
                def = (Map<String, Object>) definition;
            } catch (ClassCastException e) {
                throw new JApiSchemaParseError("Document root must be an array of objects", e);
            }
            String schemaKey = findSchemaKey(def);
            if (schemaKeys.contains(schemaKey)) {
                duplicateKeys.add(schemaKey);
            }
            schemaKeys.add(schemaKey);
            schemaKeysToIndex.put(schemaKey, index);
            index += 1;
        }

        if (!duplicateKeys.isEmpty()) {
            throw new JApiSchemaParseError("Schema has duplicate keys %s".formatted(duplicateKeys));
        }

        var traits = new ArrayList<UTrait>();

        var rootTypeParameterCount = 0;
        boolean allowTraitsAndInfo = true;
        for (var schemaKey : schemaKeys) {
            var typ = getOrParseType(schemaKey, rootTypeParameterCount, allowTraitsAndInfo, originalJApiSchema,
                    schemaKeysToIndex,
                    parsedTypes, typeExtensions);
            if (typ instanceof UTrait t) {
                traits.add(t);
            }
        }

        for (var trait : traits) {
            applyTraitToParsedTypes(trait, parsedTypes);
        }

        // Ensure all type extensions are defined
        for (var entry : typeExtensions.entrySet()) {
            var typeExtensionName = entry.getKey();
            var typeExtension = (UExt) parsedTypes.get(typeExtensionName);
            if (typeExtension == null) {
                throw new JApiSchemaParseError("Undefined type extension %s".formatted(typeExtensionName));
            }
        }

        return new UApiSchemaTuple(originalJApiSchema, parsedTypes);
    }

    private static String findSchemaKey(Map<String, Object> definition) {
        for (var e : definition.keySet()) {
            if (e.matches("^((fn|trait|info)|((struct|enum|ext)(<[0-2]>)?))\\..*")) {
                return e;
            }
        }
        throw new JApiSchemaParseError(
                "Invalid definition. Each definition should have one key matching the regex ^(struct|enum|fn|trait|info|ext)\\..* but was %s"
                        .formatted(definition));
    }

    static void applyTraitToParsedTypes(UTrait trait, Map<String, UType> parsedTypes) {
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
                    throw new JApiSchemaParseError(
                            "Argument field already in use: %s".formatted(newKey));
                }
                fnArgFields.put(newKey, traitArgumentField.getValue());
            }

            for (var traitResultField : traitFnResultValues.entrySet()) {
                var newKey = traitResultField.getKey();
                if (fnResultValues.containsKey(newKey)) {
                    throw new JApiSchemaParseError(
                            "Result value already in use: %s".formatted(newKey));
                }
                fnResultValues.put(newKey, traitResultField.getValue());
            }
        }
    }

    public static UTrait parseTraitType(
            Map<String, Object> traitDefinitionAsParsedJson,
            String definitionKey,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes,
            Map<String, TypeExtension> typeExtensions) {
        Map<String, Object> def;
        try {
            def = (Map<String, Object>) traitDefinitionAsParsedJson.get(definitionKey);
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError("Invalid trait definition %s".formatted(definitionKey));
        }

        String traitFunctionRegex;
        String traitFunctionKey;
        if (def.containsKey("fn.*")) {
            traitFunctionKey = "fn.*";
            traitFunctionRegex = "^fn\\.[a-zA-Z]";
        } else if (def.containsKey("fn._?*")) {
            if (!definitionKey.startsWith("trait._")) {
                throw new JApiSchemaParseError("Invalid trait definition %s".formatted(definitionKey));
            }
            traitFunctionKey = "fn._?*";
            traitFunctionRegex = "^fn\\.[a-zA-Z_]";
        } else {
            throw new JApiSchemaParseError("Invalid trait definition %s".formatted(definitionKey));
        }

        var traitFunction = parseFunctionType(def, traitFunctionKey, originalJApiSchema, schemaKeysToIndex, parsedTypes,
                typeExtensions,
                true);

        return new UTrait(definitionKey, traitFunction, traitFunctionRegex);
    }

    private static UFn parseFunctionType(
            Map<String, Object> functionDefinitionAsParsedJson,
            String definitionKey,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes,
            Map<String, TypeExtension> typeExtensions,
            boolean isForTrait) {
        Map<String, Object> argumentDefinitionAsParsedJson;
        try {
            argumentDefinitionAsParsedJson = (Map<String, Object>) functionDefinitionAsParsedJson.get(definitionKey);
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError("Invalid function definition for %s".formatted(definitionKey));
        }
        var argumentFields = new HashMap<String, UFieldDeclaration>();
        var isForEnum = false;
        var typeParameterCount = 0;
        for (var entry : argumentDefinitionAsParsedJson.entrySet()) {
            var fieldDeclaration = entry.getKey();
            var typeDeclarationValue = entry.getValue();
            var parsedField = parseField(fieldDeclaration,
                    typeDeclarationValue, isForEnum, typeParameterCount, originalJApiSchema, schemaKeysToIndex,
                    parsedTypes,
                    typeExtensions);
            argumentFields.put(parsedField.fieldName, parsedField.fieldDeclaration);
        }

        var argType = new UStruct(definitionKey, argumentFields, typeParameterCount);

        Map<String, Object> resultDefinitionAsParsedJson;
        try {
            resultDefinitionAsParsedJson = (Map<String, Object>) functionDefinitionAsParsedJson.get("->");
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError("Invalid function definition for %s".formatted(definitionKey));
        }

        if (!isForTrait) {
            if (!resultDefinitionAsParsedJson.containsKey("ok")) {
                throw new JApiSchemaParseError("Invalid function definition for %s".formatted(definitionKey));
            }
        }

        var values = new HashMap<String, UStruct>();
        for (var entry : resultDefinitionAsParsedJson.entrySet()) {
            Map<String, Object> enumValueData;
            try {
                enumValueData = (Map<String, Object>) entry.getValue();
            } catch (ClassCastException e) {
                throw new JApiSchemaParseError("Invalid function definition for %s".formatted(definitionKey));
            }
            var enumValue = entry.getKey();

            var fields = new HashMap<String, UFieldDeclaration>();
            for (var structEntry : enumValueData.entrySet()) {
                var fieldDeclaration = structEntry.getKey();
                var typeDeclarationValue = structEntry.getValue();
                var parsedField = parseField(fieldDeclaration,
                        typeDeclarationValue, isForEnum, typeParameterCount, originalJApiSchema, schemaKeysToIndex,
                        parsedTypes,
                        typeExtensions);
                fields.put(parsedField.fieldName, parsedField.fieldDeclaration);
            }

            var enumStruct = new UStruct("->.%s".formatted(enumValue), fields, typeParameterCount);

            values.put(enumValue, enumStruct);
        }

        var resultType = new UEnum("%s.->".formatted(definitionKey), values, typeParameterCount);

        var type = new UFn(definitionKey, argType, resultType);

        return type;
    }

    private static UStruct parseStructType(
            Map<String, Object> structDefinitionAsParsedJson,
            String definitionKey,
            int typeParameterCount,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes,
            Map<String, TypeExtension> typeExtensions) {
        var definition = (Map<String, Object>) structDefinitionAsParsedJson.get(definitionKey);

        var fields = new HashMap<String, UFieldDeclaration>();
        for (var entry : definition.entrySet()) {
            var fieldDeclaration = entry.getKey();
            var typeDeclarationValue = entry.getValue();
            var parsedField = parseField(fieldDeclaration,
                    typeDeclarationValue, false, typeParameterCount, originalJApiSchema, schemaKeysToIndex, parsedTypes,
                    typeExtensions);
            fields.put(parsedField.fieldName, parsedField.fieldDeclaration);
        }

        var type = new UStruct(definitionKey, fields, typeParameterCount);

        return type;
    }

    private static UEnum parseEnumType(
            Map<String, Object> enumDefinitionAsParsedJson,
            String definitionKey,
            int typeParameterCount,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes,
            Map<String, TypeExtension> typeExtensions) {
        var definition = (Map<String, Object>) enumDefinitionAsParsedJson.get(definitionKey);

        var values = new HashMap<String, UStruct>();
        for (var entry : definition.entrySet()) {
            Map<String, Object> enumStructData;
            try {
                enumStructData = (Map<String, Object>) entry.getValue();
            } catch (ClassCastException e) {
                throw new JApiSchemaParseError("Invalid enum definition for %s".formatted(definitionKey));
            }
            var enumValue = entry.getKey();

            var fields = new HashMap<String, UFieldDeclaration>();
            for (var structEntry : enumStructData.entrySet()) {
                var fieldDeclaration = structEntry.getKey();
                var typeDeclarationValue = structEntry.getValue();
                var parsedField = parseField(fieldDeclaration,
                        typeDeclarationValue, false, typeParameterCount, originalJApiSchema, schemaKeysToIndex,
                        parsedTypes,
                        typeExtensions);
                fields.put(parsedField.fieldName, parsedField.fieldDeclaration);
            }

            var enumStruct = new UStruct("%s.%s".formatted(definitionKey, enumValue), fields, typeParameterCount);

            values.put(enumValue, enumStruct);
        }

        var type = new UEnum(definitionKey, values, typeParameterCount);

        return type;
    }

    private static UFieldNameAndFieldDeclaration parseField(
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
            throw new JApiSchemaParseError("Could not parse field declaration: %s".formatted(fieldDeclaration));
        }

        String fieldName = matcher.group(1);

        boolean optional = matcher.group(2) != null;

        List<Object> typeDeclarationArray;
        try {
            typeDeclarationArray = (List<Object>) typeDeclarationValue;
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError(
                    "Type declarations should be strings: %s %s".formatted(fieldDeclaration, typeDeclarationValue));
        }

        if (optional && isForEnum) {
            throw new JApiSchemaParseError("Enum keys cannot be marked as optional");
        }

        var typeDeclaration = parseTypeDeclaration(typeDeclarationArray, typeParameterCount, originalJApiSchema,
                schemaKeysToIndex,
                parsedTypes,
                typeExtensions);

        return new UFieldNameAndFieldDeclaration(fieldName, new UFieldDeclaration(typeDeclaration, optional));
    }

    private static UTypeDeclaration parseTypeDeclaration(List<Object> typeDeclarationArray,
            int thisTypeParameterCount,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes, Map<String, TypeExtension> typeExtensions) {
        if (typeDeclarationArray.size() == 0) {
            throw new JApiSchemaParseError("Invalid type declaration: %s".formatted(typeDeclarationArray));
        }

        String rootTypeString;
        try {
            rootTypeString = (String) typeDeclarationArray.get(0);
        } catch (ClassCastException ex) {
            throw new JApiSchemaParseError("Invalid type declaration: %s".formatted(typeDeclarationArray));
        }

        var regex = Pattern.compile("^(.*?)(\\?)?$");
        var matcher = regex.matcher(rootTypeString);
        if (!matcher.find()) {
            throw new JApiSchemaParseError("Invalid type declaration: %s".formatted(typeDeclarationArray));
        }

        var typeName = matcher.group(1);
        var nullable = matcher.group(2) != null;

        boolean allowTraitsAndInfo = false;
        var type = getOrParseType(typeName, thisTypeParameterCount, allowTraitsAndInfo, originalJApiSchema,
                schemaKeysToIndex, parsedTypes,
                typeExtensions);

        if (type instanceof UGeneric && nullable) {
            throw new JApiSchemaParseError("Invalid type declaration: %s".formatted(typeDeclarationArray));
        }

        var givenTypeParameterCount = typeDeclarationArray.size() - 1;
        if (type.getTypeParameterCount() != givenTypeParameterCount) {
            throw new JApiSchemaParseError("Invalid type declaration: %s".formatted(typeDeclarationArray));
        }

        var typeParameters = new ArrayList<UTypeDeclaration>();
        var givenTypeParameters = typeDeclarationArray.subList(1, typeDeclarationArray.size());
        for (var e : givenTypeParameters) {
            List<Object> l;
            try {
                l = (List<Object>) e;
            } catch (ClassCastException ex) {
                throw new JApiSchemaParseError("Invalid type declaration: %s".formatted(typeDeclarationArray));
            }
            var typeParameterTypeDeclaration = parseTypeDeclaration(l, thisTypeParameterCount, originalJApiSchema,
                    schemaKeysToIndex, parsedTypes, typeExtensions);
            typeParameters.add(typeParameterTypeDeclaration);
        }

        return new UTypeDeclaration(type, nullable, typeParameters);
    }

    private static UType getOrParseType(String typeName, int thisTypeParameterCount, boolean allowTraitsAndInfo,
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
            throw new JApiSchemaParseError("Unrecognized type: %s".formatted(typeName));
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
                            throw new JApiSchemaParseError(
                                    "Generic index (%d) too high for this type: %s".formatted(genericParameterIndex,
                                            typeName));
                        }
                        yield new UGeneric(genericParameterIndex);
                    } else {
                        throw new JApiSchemaParseError("Unrecognized type: %s".formatted(typeName));
                    }
                }
            };
        }

        var customTypeName = matcher.group(3);
        if (customTypeName != null) {
            var index = schemaKeysToIndex.get(customTypeName);
            if (index == null) {
                throw new JApiSchemaParseError("Unrecognized type: %s".formatted(typeName));
            }
            var definition = (Map<String, Object>) originalJApiSchema.get(index);

            var typeParameterCountString = matcher.group(7);
            int typeParameterCount = 0;
            if (typeParameterCountString != null) {
                try {
                    typeParameterCount = Integer.parseInt(typeParameterCountString);
                } catch (NumberFormatException e) {
                    throw new JApiSchemaParseError(
                            "Type parameter count must match regex (<([1-3])>)?".formatted(standardTypeName));
                }
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
                    throw new JApiSchemaParseError(
                            "Missing type extension implementation %s".formatted(customTypeName));
                }
                type = new UExt(customTypeName, typeExtension, typeParameterCount);
            } else {
                throw new JApiSchemaParseError("Unrecognized type: %s".formatted(customTypeName));
            }

            parsedTypes.put(customTypeName, type);

            return type;
        }

        throw new JApiSchemaParseError("Invalid type: %s".formatted(typeName));
    }
}
