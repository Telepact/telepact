package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

class _ParseSchemaCustomTypeUtil {

    static UStruct parseStructType(
            List<Object> path,
            Map<String, Object> structDefinitionAsParsedJson,
            String schemaKey,
            int typeParameterCount,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes,
            Map<String, TypeExtension> typeExtensions, List<SchemaParseFailure> allParseFailures,
            Set<String> failedTypes) {
        var thisPath = _ValidateUtil.append(path, schemaKey);

        Object defInit = structDefinitionAsParsedJson.get(schemaKey);

        Map<String, Object> definition;
        try {
            definition = _CastUtil.asMap(defInit);
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError(
                    _ParseSchemaUtil.getTypeUnexpectedValidationFailure(thisPath, defInit, "Object"));
        }

        var parseFailures = new ArrayList<SchemaParseFailure>();

        var fields = new HashMap<String, UFieldDeclaration>();
        for (var entry : definition.entrySet()) {
            var fieldDeclaration = entry.getKey();
            var typeDeclarationValue = entry.getValue();
            try {
                var parsedField = parseField(thisPath, fieldDeclaration,
                        typeDeclarationValue, typeParameterCount, originalJApiSchema, schemaKeysToIndex,
                        parsedTypes,
                        typeExtensions, allParseFailures, failedTypes);
                String fieldName = parsedField.fieldName;
                fields.put(fieldName, parsedField);
            } catch (JApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new JApiSchemaParseError(parseFailures);
        }

        var type = new UStruct(schemaKey, fields, typeParameterCount);

        return type;
    }

    static UUnion parseUnionType(
            List<Object> path,
            Map<String, Object> unionDefinitionAsParsedJson,
            String schemaKey,
            boolean okCaseRequired,
            int typeParameterCount,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes,
            Map<String, TypeExtension> typeExtensions, List<SchemaParseFailure> allParseFailures,
            Set<String> failedTypes) {
        var thisPath = _ValidateUtil.append(path, schemaKey);

        Object defInit = unionDefinitionAsParsedJson.get(schemaKey);

        Map<String, Object> definition;
        try {
            definition = _CastUtil.asMap(defInit);
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError(
                    _ParseSchemaUtil.getTypeUnexpectedValidationFailure(thisPath, defInit, "Object"));
        }

        var parseFailures = new ArrayList<SchemaParseFailure>();

        var cases = new HashMap<String, UStruct>();

        if (okCaseRequired) {
            if (!definition.containsKey("Ok")) {
                throw new JApiSchemaParseError(List.of(new SchemaParseFailure(_ValidateUtil.append(thisPath, "Ok"),
                        "RequiredObjectKeyMissing", Map.of())));
            }
        }

        for (var entry : definition.entrySet()) {
            var unionCase = entry.getKey();

            var unionKeyPath = _ValidateUtil.append(thisPath, unionCase);

            var regexString = "^(_?[A-Z][a-zA-Z0-9_]*)$";
            var regex = Pattern.compile(regexString);
            var matcher = regex.matcher(unionCase);
            if (!matcher.find()) {
                parseFailures.add(new SchemaParseFailure(unionKeyPath,
                        "KeyRegexMatchFailed", Map.of("regex", regexString)));
                continue;
            }

            Map<String, Object> unionCaseStruct;
            try {
                unionCaseStruct = _CastUtil.asMap(entry.getValue());
            } catch (ClassCastException e) {
                parseFailures.addAll(
                        _ParseSchemaUtil.getTypeUnexpectedValidationFailure(unionKeyPath, entry.getValue(), "Object"));
                continue;
            }

            var fields = new HashMap<String, UFieldDeclaration>();
            for (var structEntry : unionCaseStruct.entrySet()) {
                var fieldDeclaration = structEntry.getKey();
                var typeDeclarationValue = structEntry.getValue();
                UFieldDeclaration parsedField;
                try {
                    parsedField = parseField(_ValidateUtil.append(thisPath, unionCase), fieldDeclaration,
                            typeDeclarationValue, typeParameterCount, originalJApiSchema, schemaKeysToIndex,
                            parsedTypes,
                            typeExtensions, allParseFailures, failedTypes);
                    String fieldName = parsedField.fieldName;
                    fields.put(fieldName, parsedField);
                } catch (JApiSchemaParseError e) {
                    parseFailures.addAll(e.schemaParseFailures);
                }
            }

            var unionStruct = new UStruct("%s.%s".formatted(schemaKey, unionCase), fields, typeParameterCount);

            cases.put(unionCase, unionStruct);
        }

        if (!parseFailures.isEmpty()) {
            throw new JApiSchemaParseError(parseFailures);
        }

        var type = new UUnion(schemaKey, cases, typeParameterCount);

        return type;
    }

    static UFieldDeclaration parseField(
            List<Object> path,
            String fieldDeclaration,
            Object typeDeclarationValue,
            int typeParameterCount,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes,
            Map<String, TypeExtension> typeExtensions, List<SchemaParseFailure> allParseFailures,
            Set<String> failedTypes) {
        var regexString = "^(_?[a-z][a-zA-Z0-9_]*)(!)?$";
        var regex = Pattern.compile(regexString);
        var matcher = regex.matcher(fieldDeclaration);
        if (!matcher.find()) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "KeyRegexMatchFailed", Map.of("regex", regexString))));
        }

        String fieldName = matcher.group(0);

        boolean optional = matcher.group(2) != null;

        var thisPath = _ValidateUtil.append(path, fieldName);

        List<Object> typeDeclarationArray;
        try {
            typeDeclarationArray = _CastUtil.asList(typeDeclarationValue);
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError(
                    _ParseSchemaUtil.getTypeUnexpectedValidationFailure(thisPath, typeDeclarationValue, "Array"));
        }

        var typeDeclaration = _ParseSchemaTypeUtil.parseTypeDeclaration(thisPath,
                typeDeclarationArray, typeParameterCount,
                originalJApiSchema,
                schemaKeysToIndex,
                parsedTypes,
                typeExtensions, allParseFailures, failedTypes);

        return new UFieldDeclaration(fieldName, typeDeclaration, optional);
    }
}
