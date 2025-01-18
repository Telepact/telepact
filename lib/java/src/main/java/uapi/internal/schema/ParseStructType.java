package uapi.internal.schema;

import static uapi.internal.schema.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static uapi.internal.schema.ParseStructFields.parseStructFields;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;

import uapi.UApiSchemaParseError;
import uapi.internal.types.UStruct;

public class ParseStructType {
    static UStruct parseStructType(
            List<Object> path,
            Map<String, Object> structDefinitionAsPseudoJson,
            String schemaKey, List<String> ignoreKeys,
            ParseContext ctx) {
        final var parseFailures = new ArrayList<SchemaParseFailure>();
        final var otherKeys = new HashSet<>(structDefinitionAsPseudoJson.keySet());

        otherKeys.remove(schemaKey);
        otherKeys.remove("///");
        otherKeys.remove("_ignoreIfDuplicate");
        for (final var ignoreKey : ignoreKeys) {
            otherKeys.remove(ignoreKey);
        }

        if (otherKeys.size() > 0) {
            for (final var k : otherKeys) {
                final List<Object> loopPath = new ArrayList<>(path);
                loopPath.add(k);

                parseFailures.add(new SchemaParseFailure(ctx.documentName, loopPath, "ObjectKeyDisallowed", Map.of()));
            }
        }

        final List<Object> thisPath = new ArrayList<>(path);
        thisPath.add(schemaKey);

        final Object defInit = structDefinitionAsPseudoJson.get(schemaKey);

        Map<String, Object> definition = null;
        if (!(defInit instanceof Map)) {
            final List<SchemaParseFailure> branchParseFailures = getTypeUnexpectedParseFailure(ctx.documentName,
                    thisPath,
                    defInit, "Object");

            parseFailures.addAll(branchParseFailures);
        } else {
            definition = (Map<String, Object>) defInit;
        }

        if (parseFailures.size() > 0) {
            throw new UApiSchemaParseError(parseFailures, ctx.uApiSchemaDocumentNamesToJson);
        }

        final var fields = parseStructFields(thisPath, definition, ctx);

        return new UStruct(schemaKey, fields);
    }
}
