package io.github.brenbar.uapi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

class _ParseSchemaTraitUtil {
    static void applyTraitToParsedTypes(UTrait trait, Map<String, _UType> parsedTypes,
            Map<String, Integer> schemaKeysToIndex) {
        String traitName = trait.name;
        var traitIndex = schemaKeysToIndex.get(traitName);

        var parseFailures = new ArrayList<SchemaParseFailure>();
        for (var parsedType : parsedTypes.entrySet()) {
            _UFn f;
            try {
                f = (_UFn) parsedType.getValue();
            } catch (ClassCastException e) {
                continue;
            }

            String fnName = f.name;

            var regex = Pattern.compile(f.extendsRegex);
            var matcher = regex.matcher(traitName);
            if (!matcher.find()) {
                continue;
            }

            _UUnion fnResult = f.result;
            Map<String, _UStruct> fnResultCases = fnResult.cases;
            _UUnion traitFnResult = trait.errors;
            Map<String, _UStruct> traitFnResultCases = traitFnResult.cases;

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
            throw new UApiSchemaParseError(parseFailures);
        }
    }

    public static UTrait parseTraitType(
            Map<String, Object> traitDefinitionAsParsedJson,
            String schemaKey,
            List<Object> originalUApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, _UType> parsedTypes,
            Map<String, _UType> typeExtensions, List<SchemaParseFailure> allParseFailures,
            Set<String> failedTypes) {
        var index = schemaKeysToIndex.get(schemaKey);
        List<Object> thisPath = List.of(index, schemaKey);

        var mapInit = traitDefinitionAsParsedJson.get(schemaKey);

        Map<String, Object> def;
        try {
            def = _CastUtil.asMap(mapInit);
        } catch (ClassCastException e) {
            throw new UApiSchemaParseError(
                    _ParseSchemaUtil.getTypeUnexpectedValidationFailure(thisPath, mapInit, "Object"));
        }

        var errorPath = _ValidateUtil.append(thisPath, "->");

        if (!def.containsKey("->")) {
            throw new UApiSchemaParseError(
                    List.of(new SchemaParseFailure(errorPath, "RequiredObjectKeyMissing", Map.of())));
        }

        var trait = _ParseSchemaCustomTypeUtil.parseUnionType(thisPath, def, "->",
                false, 0, originalUApiSchema,
                schemaKeysToIndex, parsedTypes,
                typeExtensions,
                allParseFailures, failedTypes);

        return new UTrait(schemaKey, trait);
    }
}
