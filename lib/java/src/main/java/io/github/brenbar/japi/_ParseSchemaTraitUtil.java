package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

class _ParseSchemaTraitUtil {
    static void applyTraitToParsedTypes(UTrait trait, Map<String, UType> parsedTypes,
            Map<String, Integer> schemaKeysToIndex) {
        String traitName = trait.name;
        var traitIndex = schemaKeysToIndex.get(traitName);

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

            UStruct fnArg = f.call.cases.get(f.name);
            Map<String, UFieldDeclaration> fnArgFields = fnArg.fields;
            UUnion fnResult = f.result;
            Map<String, UStruct> fnResultValues = fnResult.cases;
            UFn traitFn = trait.fn;
            String traitFnName = traitFn.name;
            UStruct traitFnArg = traitFn.call.cases.get(traitFn.name);
            Map<String, UFieldDeclaration> traitFnArgFields = traitFnArg.fields;
            UUnion traitFnResult = traitFn.result;
            Map<String, UStruct> traitFnResultValues = traitFnResult.cases;

            if (fnName.startsWith("fn._")) {
                // Only internal traits can change internal functions
                if (!traitName.startsWith("trait._")) {
                    continue;
                }
            }

            for (var traitArgumentField : traitFnArgFields.entrySet()) {
                var newKey = traitArgumentField.getKey();
                if (fnArgFields.containsKey(newKey)) {
                    var otherPathIndex = schemaKeysToIndex.get(fnName);
                    parseFailures.add(
                            new SchemaParseFailure(
                                    List.of(traitIndex, traitName, traitFnName, newKey),
                                    "PathCollision", Map.of("other", List.of(otherPathIndex, fnName, newKey))));
                }
                fnArgFields.put(newKey, traitArgumentField.getValue());
            }

            for (var traitResultField : traitFnResultValues.entrySet()) {
                var newKey = traitResultField.getKey();
                if (fnResultValues.containsKey(newKey)) {
                    var otherPathIndex = schemaKeysToIndex.get(fnName);
                    parseFailures.add(new SchemaParseFailure(List.of(traitIndex, traitName, "->", newKey),
                            "PathCollision", Map.of("other", List.of(otherPathIndex, "->", newKey))));
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
            Map<String, TypeExtension> typeExtensions, List<SchemaParseFailure> allParseFailures,
            Set<String> failedTypes) {
        var index = schemaKeysToIndex.get(schemaKey);
        List<Object> thisPath = List.of(index, schemaKey);

        var defInit = traitDefinitionAsParsedJson.get(schemaKey);

        Map<String, Object> def;
        try {
            def = _CastUtil.asMap(defInit);
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError(
                    _ParseSchemaUtil.getTypeUnexpectedValidationFailure(thisPath, defInit, "Object"));
        }

        String traitFunctionRegex;
        String traitFunctionKey;
        if (def.containsKey("fn.*")) {
            traitFunctionKey = "fn.*";
            traitFunctionRegex = "^fn\\.[a-zA-Z]";
        } else if (def.containsKey("fn._?*")) {
            if (!schemaKey.startsWith("trait._")) {
                throw new JApiSchemaParseError(List.of(new SchemaParseFailure(_ValidateUtil.append(thisPath, "fn.*"),
                        "RequiredObjectKeyMissing", Map.of())));
            }
            traitFunctionKey = "fn._?*";
            traitFunctionRegex = "^fn\\.[a-zA-Z_]";
        } else {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(_ValidateUtil.append(thisPath, "fn.*"),
                    "RequiredObjectKeyMissing", Map.of())));
        }

        var traitFunction = _ParseSchemaFnTypeUtil.parseFunctionType(thisPath, def, traitFunctionKey,
                originalJApiSchema,
                schemaKeysToIndex, parsedTypes,
                typeExtensions,
                true, allParseFailures, failedTypes);

        return new UTrait(schemaKey, traitFunction, traitFunctionRegex);
    }
}
