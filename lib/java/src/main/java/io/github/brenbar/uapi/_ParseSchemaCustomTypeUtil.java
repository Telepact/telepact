package io.github.brenbar.uapi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

class _ParseSchemaCustomTypeUtil {

    static _UStruct parseStructType(List<Object> path, Map<String, Object> structDefinitionAsPseudoJson,
            String schemaKey, int typeParameterCount, List<Object> originalUApiSchema,
            Map<String, Integer> schemaKeysToIndex, Map<String, _UType> parsedTypes, Map<String, _UType> typeExtensions,
            List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        final List<Object> thisPath = _ValidateUtil.append(path, schemaKey);
        final Object defInit = structDefinitionAsPseudoJson.get(schemaKey);

        final Map<String, Object> definition;
        try {
            definition = _CastUtil.asMap(defInit);
        } catch (ClassCastException e) {
            final List<SchemaParseFailure> finalParseFailures = _ParseSchemaUtil
                    .getTypeUnexpectedValidationFailure(thisPath, defInit, "Object");
            throw new UApiSchemaParseError(finalParseFailures);
        }

        final var fields = parseStructFields(definition, thisPath, typeParameterCount,
                originalUApiSchema, schemaKeysToIndex, parsedTypes, typeExtensions, allParseFailures,
                failedTypes);

        return new _UStruct(schemaKey, fields, typeParameterCount);
    }

    static _UUnion parseUnionType(List<Object> path, Map<String, Object> unionDefinitionAsPseudoJson, String schemaKey,
            boolean okCaseRequired, int typeParameterCount, List<Object> originalUApiSchema,
            Map<String, Integer> schemaKeysToIndex, Map<String, _UType> parsedTypes, Map<String, _UType> typeExtensions,
            List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        final List<Object> thisPath = _ValidateUtil.append(path, schemaKey);
        Object defInit = unionDefinitionAsPseudoJson.get(schemaKey);

        final Map<String, Object> definition;
        try {
            definition = _CastUtil.asMap(defInit);
        } catch (ClassCastException e) {
            final List<SchemaParseFailure> finalParseFailures = _ParseSchemaUtil
                    .getTypeUnexpectedValidationFailure(thisPath, defInit, "Object");
            throw new UApiSchemaParseError(finalParseFailures);
        }

        final var parseFailures = new ArrayList<SchemaParseFailure>();
        final var cases = new HashMap<String, _UStruct>();

        if (okCaseRequired) {
            if (!definition.containsKey("Ok")) {
                final List<Object> finalPath = _ValidateUtil.append(thisPath, "Ok");
                throw new UApiSchemaParseError(List.of(new SchemaParseFailure(finalPath,
                        "RequiredObjectKeyMissing", Map.of())));
            }
        }

        for (final var entry : definition.entrySet()) {
            final var unionCase = entry.getKey();
            final List<Object> unionKeyPath = _ValidateUtil.append(thisPath, unionCase);
            final var regexString = "^(_?[A-Z][a-zA-Z0-9_]*)$";
            final var regex = Pattern.compile(regexString);

            final var matcher = regex.matcher(unionCase);
            if (!matcher.find()) {
                parseFailures.add(new SchemaParseFailure(unionKeyPath,
                        "KeyRegexMatchFailed", Map.of("regex", regexString)));
                continue;
            }

            final Map<String, Object> unionCaseStruct;
            try {
                unionCaseStruct = _CastUtil.asMap(entry.getValue());
            } catch (ClassCastException e) {
                List<SchemaParseFailure> thisParseFailures = _ParseSchemaUtil
                        .getTypeUnexpectedValidationFailure(unionKeyPath, entry.getValue(), "Object");

                parseFailures.addAll(thisParseFailures);
                continue;
            }

            final Map<String, _UFieldDeclaration> fields;
            try {
                fields = parseStructFields(unionCaseStruct, unionKeyPath, typeParameterCount,
                        originalUApiSchema, schemaKeysToIndex, parsedTypes, typeExtensions, allParseFailures,
                        failedTypes);
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
                continue;
            }

            final var unionStruct = new _UStruct("%s.%s".formatted(schemaKey, unionCase), fields, typeParameterCount);

            cases.put(unionCase, unionStruct);
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }

        return new _UUnion(schemaKey, cases, typeParameterCount);
    }

    static Map<String, _UFieldDeclaration> parseStructFields(Map<String, Object> referenceStruct, List<Object> path,
            int typeParameterCount, List<Object> originalUApiSchema, Map<String, Integer> schemaKeysToIndex,
            Map<String, _UType> parsedTypes, Map<String, _UType> typeExtensions,
            List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        final var parseFailures = new ArrayList<SchemaParseFailure>();
        final var fields = new HashMap<String, _UFieldDeclaration>();

        for (final var structEntry : referenceStruct.entrySet()) {
            final var fieldDeclaration = structEntry.getKey();

            for (final var existingField : fields.keySet()) {
                final var existingFieldNoOpt = existingField.split("!")[0];
                final var fieldNoOpt = fieldDeclaration.split("!")[0];
                if (fieldNoOpt.equals(existingFieldNoOpt)) {
                    final List<Object> finalPath = _ValidateUtil.append(path, fieldDeclaration);
                    final List<Object> finalOtherPath = _ValidateUtil.append(path, existingField);

                    parseFailures
                            .add(new SchemaParseFailure(finalPath, "PathCollision",
                                    Map.of("other", finalOtherPath)));
                }
            }

            final var typeDeclarationValue = structEntry.getValue();

            final _UFieldDeclaration parsedField;
            try {
                parsedField = parseField(path, fieldDeclaration,
                        typeDeclarationValue, typeParameterCount, originalUApiSchema, schemaKeysToIndex,
                        parsedTypes,
                        typeExtensions, allParseFailures, failedTypes);
                final String fieldName = parsedField.fieldName;

                fields.put(fieldName, parsedField);
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }

        return fields;
    }

    static _UFieldDeclaration parseField(List<Object> path, String fieldDeclaration, Object typeDeclarationValue,
            int typeParameterCount, List<Object> originalUApiSchema, Map<String, Integer> schemaKeysToIndex,
            Map<String, _UType> parsedTypes, Map<String, _UType> typeExtensions,
            List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        final var regexString = "^(_?[a-z][a-zA-Z0-9_]*)(!)?$";
        final var regex = Pattern.compile(regexString);

        final var matcher = regex.matcher(fieldDeclaration);
        if (!matcher.find()) {
            final List<Object> finalPath = _ValidateUtil.append(path, fieldDeclaration);
            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(finalPath,
                    "KeyRegexMatchFailed", Map.of("regex", regexString))));
        }

        final var fieldName = matcher.group(0);
        final var optional = matcher.group(2) != null;
        final List<Object> thisPath = _ValidateUtil.append(path, fieldName);

        final List<Object> typeDeclarationArray;
        try {
            typeDeclarationArray = _CastUtil.asList(typeDeclarationValue);
        } catch (ClassCastException e) {
            throw new UApiSchemaParseError(
                    _ParseSchemaUtil.getTypeUnexpectedValidationFailure(thisPath, typeDeclarationValue, "Array"));
        }

        final var typeDeclaration = _ParseSchemaTypeUtil.parseTypeDeclaration(thisPath,
                typeDeclarationArray, typeParameterCount,
                originalUApiSchema,
                schemaKeysToIndex,
                parsedTypes,
                typeExtensions, allParseFailures, failedTypes);

        return new _UFieldDeclaration(fieldName, typeDeclaration, optional);
    }
}
