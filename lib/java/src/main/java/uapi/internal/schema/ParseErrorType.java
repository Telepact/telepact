package uapi.internal.schema;

import static uapi.internal.schema.ParseUnionType.parseUnionType;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import uapi.UApiSchemaParseError;
import uapi.internal.types.UError;
import uapi.internal.types.UType;
import uapi.internal.types.UUnion;

public class ParseErrorType {
    public static UError parseErrorType(Map<String, Object> errorDefinitionAsParsedJson,
            List<Object> uApiSchemaPseudoJson,
            String schemaKey,
            int index,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes,
            List<SchemaParseFailure> allParseFailures,
            Set<String> failedTypes) {
        List<Object> basePath = new ArrayList<>();
        basePath.add(index);

        List<SchemaParseFailure> parseFailures = new ArrayList<>();

        Set<String> otherKeys = new HashSet<>(errorDefinitionAsParsedJson.keySet());
        otherKeys.remove(schemaKey);
        otherKeys.remove("///");

        if (!otherKeys.isEmpty()) {
            for (String k : otherKeys) {
                List<Object> loopPath = new ArrayList<>(basePath);
                loopPath.add(k);
                parseFailures.add(new SchemaParseFailure(loopPath, "ObjectKeyDisallowed", new HashMap<>(), null));
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }

        int typeParameterCount = 0;

        // Assuming parseUnionType is adapted to Java and returns UError or its

        UUnion error = parseUnionType(basePath, errorDefinitionAsParsedJson, schemaKey,
                new ArrayList<>(),
                new ArrayList<>(), typeParameterCount, uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes,
                allParseFailures, failedTypes);

        return new UError(schemaKey, error);
    }
}
