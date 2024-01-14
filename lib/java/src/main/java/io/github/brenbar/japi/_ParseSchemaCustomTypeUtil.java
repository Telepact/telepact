package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

class _ParseSchemaCustomTypeUtil {

    static _UStruct parseStructType(
            List<Object> path,
            Map<String, Object> structDefinitionAsParsedJson,
            String schemaKey,
            int typeParameterCount,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, _UType> parsedTypes,
            Map<String, _UType> typeExtensions, List<SchemaParseFailure> allParseFailures,
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

        var fields = parseStructFields(definition, thisPath, typeParameterCount,
                originalJApiSchema, schemaKeysToIndex, parsedTypes, typeExtensions, allParseFailures,
                failedTypes);

        var type = new _UStruct(schemaKey, fields, typeParameterCount);

        return type;
    }

    static _UUnion parseUnionType(
            List<Object> path,
            Map<String, Object> unionDefinitionAsParsedJson,
            String schemaKey,
            boolean okCaseRequired,
            int typeParameterCount,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, _UType> parsedTypes,
            Map<String, _UType> typeExtensions, List<SchemaParseFailure> allParseFailures,
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

        var cases = new HashMap<String, _UStruct>();

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

            Map<String, _UFieldDeclaration> fields;
            try {
                fields = parseStructFields(unionCaseStruct, unionKeyPath, typeParameterCount,
                        originalJApiSchema, schemaKeysToIndex, parsedTypes, typeExtensions, allParseFailures,
                        failedTypes);
            } catch (JApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
                continue;
            }

            var unionStruct = new _UStruct("%s.%s".formatted(schemaKey, unionCase), fields, typeParameterCount);

            cases.put(unionCase, unionStruct);
        }

        if (!parseFailures.isEmpty()) {
            throw new JApiSchemaParseError(parseFailures);
        }

        var type = new _UUnion(schemaKey, cases, typeParameterCount);

        return type;
    }

    static Map<String, _UFieldDeclaration> parseStructFields(Map<String, Object> referenceStruct, List<Object> path,
            int typeParameterCount,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, _UType> parsedTypes,
            Map<String, _UType> typeExtensions, List<SchemaParseFailure> allParseFailures,
            Set<String> failedTypes) {

        var parseFailures = new ArrayList<SchemaParseFailure>();

        var fields = new HashMap<String, _UFieldDeclaration>();
        for (var structEntry : referenceStruct.entrySet()) {
            var fieldDeclaration = structEntry.getKey();

            for (var existingField : fields.keySet()) {
                var existingFieldNoOpt = existingField.split("!")[0];
                var fieldNoOpt = fieldDeclaration.split("!")[0];
                if (fieldNoOpt.equals(existingFieldNoOpt)) {
                    parseFailures
                            .add(new SchemaParseFailure(_ValidateUtil.append(path, fieldDeclaration), "PathCollision",
                                    Map.of("other", _ValidateUtil.append(path, existingField))));
                }
            }

            var typeDeclarationValue = structEntry.getValue();
            _UFieldDeclaration parsedField;
            try {
                parsedField = parseField(path, fieldDeclaration,
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

        return fields;
    }

    static _UFieldDeclaration parseField(
            List<Object> path,
            String fieldDeclaration,
            Object typeDeclarationValue,
            int typeParameterCount,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, _UType> parsedTypes,
            Map<String, _UType> typeExtensions, List<SchemaParseFailure> allParseFailures,
            Set<String> failedTypes) {
        var regexString = "^(_?[a-z][a-zA-Z0-9_]*)(!)?$";
        var regex = Pattern.compile(regexString);
        var matcher = regex.matcher(fieldDeclaration);
        if (!matcher.find()) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(_ValidateUtil.append(path, fieldDeclaration),
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

        return new _UFieldDeclaration(fieldName, typeDeclaration, optional);
    }
}
