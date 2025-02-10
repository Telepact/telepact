package uapi.internal.schema;

import uapi.internal.types.UFieldDeclaration;
import uapi.internal.types.UHeaders;
import uapi.UApiSchemaParseError;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import static uapi.internal.schema.ParseStructFields.parseStructFields;

public class ParseHeadersType {

    public static UHeaders parseHeadersType(
            List<Object> path,
            Map<String, Object> headersDefinitionAsParsedJson,
            String schemaKey,
            ParseContext ctx) throws UApiSchemaParseError {
        List<SchemaParseFailure> parseFailures = new ArrayList<>();
        Map<String, UFieldDeclaration> requestHeaders = new HashMap<>();
        Map<String, UFieldDeclaration> responseHeaders = new HashMap<>();

        Object requestHeadersDef = headersDefinitionAsParsedJson.get(schemaKey);

        List<Object> thisPath = new ArrayList<>(path);
        thisPath.add(schemaKey);

        if (!(requestHeadersDef instanceof Map)) {
            List<SchemaParseFailure> branchParseFailures = GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure(
                    ctx.documentName,
                    thisPath,
                    requestHeadersDef,
                    "Object");
            parseFailures.addAll(branchParseFailures);
        } else {
            try {
                Map<String, UFieldDeclaration> requestFields = parseStructFields(thisPath,
                        (Map<String, Object>) requestHeadersDef, ctx);

                // All headers are optional
                final var finalRequestFields = requestFields.entrySet().stream()
                        .collect(Collectors.toMap(e -> e.getKey(), e -> new UFieldDeclaration(e.getValue().fieldName,
                                e.getValue().typeDeclaration, true)));

                requestHeaders.putAll(finalRequestFields);
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        String responseKey = "->";
        List<Object> responsePath = new ArrayList<>(path);
        responsePath.add(responseKey);

        if (!headersDefinitionAsParsedJson.containsKey(responseKey)) {
            parseFailures.add(
                    new SchemaParseFailure(ctx.documentName, responsePath, "RequiredObjectKeyMissing",
                            Map.of("key", responseKey)));
        }

        Object responseHeadersDef = headersDefinitionAsParsedJson.get(responseKey);

        if (!(responseHeadersDef instanceof Map)) {
            List<SchemaParseFailure> branchParseFailures = GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure(
                    ctx.documentName,
                    thisPath,
                    responseHeadersDef,
                    "Object");
            parseFailures.addAll(branchParseFailures);
        } else {
            try {
                Map<String, UFieldDeclaration> responseFields = ParseStructFields.parseStructFields(responsePath,
                        (Map<String, Object>) responseHeadersDef, ctx);

                // All headers are optional
                final var finalResponseFields = responseFields.entrySet().stream()
                        .collect(Collectors.toMap(e -> e.getKey(), e -> new UFieldDeclaration(e.getValue().fieldName,
                                e.getValue().typeDeclaration, true)));

                responseHeaders.putAll(finalResponseFields);
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures, ctx.uApiSchemaDocumentNamesToJson);
        }

        return new UHeaders(schemaKey, requestHeaders, responseHeaders);
    }
}
