package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

public class _ParseSchemaTraitTypeUtil {
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
            UStruct fnArg = f.call.values.get(f.name);
            Map<String, UFieldDeclaration> fnArgFields = fnArg.fields;
            UUnion fnResult = f.result;
            Map<String, UStruct> fnResultValues = fnResult.values;
            UFn traitFn = trait.fn;
            String traitFnName = traitFn.name;
            UStruct traitFnArg = traitFn.call.values.get(traitFn.name);
            Map<String, UFieldDeclaration> traitFnArgFields = traitFnArg.fields;
            UUnion traitFnResult = traitFn.result;
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
                    parseFailures.add(
                            new SchemaParseFailure("[%d].%s.%s.%s".formatted(index, traitName, traitFnName, newKey),
                                    "TraitArgumentFieldAlreadyInUseByFunction", Map.of("fn", fnName)));
                }
                fnArgFields.put(newKey, traitArgumentField.getValue());
            }

            for (var traitResultField : traitFnResultValues.entrySet()) {
                var newKey = traitResultField.getKey();
                if (fnResultValues.containsKey(newKey)) {
                    var index = schemaKeysToIndex.get(traitName);
                    parseFailures.add(new SchemaParseFailure("[%d].%s.->.%s".formatted(index, traitName, newKey),
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
                    "InvalidTrait", Map.of())));
        }

        var traitFunction = _ParseSchemaFnTypeUtil.parseFunctionType(def, traitFunctionKey, originalJApiSchema,
                schemaKeysToIndex, parsedTypes,
                typeExtensions,
                true);

        return new UTrait(schemaKey, traitFunction, traitFunctionRegex);
    }
}
