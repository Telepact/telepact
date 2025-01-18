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
import uapi.internal.types.UUnion;

public class ParseErrorType {
    public static UError parseErrorType(
            List<Object> path,
            Map<String, Object> errorDefinitionAsParsedJson,
            String schemaKey,
            ParseContext ctx) {

        List<SchemaParseFailure> parseFailures = new ArrayList<>();

        Set<String> otherKeys = new HashSet<>(errorDefinitionAsParsedJson.keySet());
        otherKeys.remove(schemaKey);
        otherKeys.remove("///");

        if (!otherKeys.isEmpty()) {
            for (String k : otherKeys) {
                List<Object> loopPath = new ArrayList<>(path);
                loopPath.add(k);
                parseFailures
                        .add(new SchemaParseFailure(ctx.documentName, loopPath, "ObjectKeyDisallowed",
                                new HashMap<>()));
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures, ctx.uApiSchemaDocumentNamesToJson);
        }

        // Assuming parseUnionType is adapted to Java and returns UError or its

        UUnion error = parseUnionType(path, errorDefinitionAsParsedJson, schemaKey,
                new ArrayList<>(),
                new ArrayList<>(), ctx);

        return new UError(schemaKey, error);
    }
}
