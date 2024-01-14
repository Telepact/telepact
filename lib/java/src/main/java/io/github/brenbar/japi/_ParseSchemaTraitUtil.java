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

            String fnName = f.name;

            var regex = Pattern.compile(f.extendsRegex);
            var matcher = regex.matcher(traitName);
            if (!matcher.find()) {
                continue;
            }

            UUnion fnResult = f.result;
            Map<String, UStruct> fnResultCases = fnResult.cases;
            UUnion traitFnResult = trait.errors;
            Map<String, UStruct> traitFnResultCases = traitFnResult.cases;

            if (fnName.startsWith("fn._")) {
                // Only internal traits can change internal functions
                if (!traitName.startsWith("trait._")) {
                    continue;
                }
            }

            for (var traitResultField : traitFnResultCases.entrySet()) {
                var newKey = traitResultField.getKey();
                if (fnResultCases.containsKey(newKey)) {
                    var otherPathIndex = schemaKeysToIndex.get(fnName);
                    parseFailures.add(new SchemaParseFailure(List.of(traitIndex, traitName, "->", newKey),
                            "PathCollision", Map.of("other", List.of(otherPathIndex, "->", newKey))));
                }
                fnResultCases.put(newKey, traitResultField.getValue());
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
            Map<String, UType> typeExtensions, List<SchemaParseFailure> allParseFailures,
            Set<String> failedTypes) {
        var index = schemaKeysToIndex.get(schemaKey);
        List<Object> thisPath = List.of(index, schemaKey);

        var mapInit = traitDefinitionAsParsedJson.get(schemaKey);

        Map<String, Object> def;
        try {
            def = _CastUtil.asMap(mapInit);
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError(
                    _ParseSchemaUtil.getTypeUnexpectedValidationFailure(thisPath, mapInit, "Object"));
        }

        var errorPath = _ValidateUtil.append(thisPath, "->");

        if (!def.containsKey("->")) {
            throw new JApiSchemaParseError(
                    List.of(new SchemaParseFailure(errorPath, "RequiredObjectKeyMissing", Map.of())));
        }

        var trait = _ParseSchemaCustomTypeUtil.parseUnionType(thisPath, def, "->",
                false, 0, originalJApiSchema,
                schemaKeysToIndex, parsedTypes,
                typeExtensions,
                allParseFailures, failedTypes);

        return new UTrait(schemaKey, trait);
    }
}
