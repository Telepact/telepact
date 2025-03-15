package io.github.msgpact.internal.schema;

import static io.github.msgpact.internal.schema.ParseStructFields.parseStructFields;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import io.github.msgpact.MsgPactSchemaParseError;
import io.github.msgpact.internal.types.VFieldDeclaration;
import io.github.msgpact.internal.types.VHeaders;

public class ParseHeadersType {

    public static VHeaders parseHeadersType(
            List<Object> path,
            Map<String, Object> headersDefinitionAsParsedJson,
            String schemaKey,
            ParseContext ctx) throws MsgPactSchemaParseError {
        List<SchemaParseFailure> parseFailures = new ArrayList<>();
        Map<String, VFieldDeclaration> requestHeaders = new HashMap<>();
        Map<String, VFieldDeclaration> responseHeaders = new HashMap<>();

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
                Map<String, VFieldDeclaration> requestFields = parseStructFields(thisPath,
                        (Map<String, Object>) requestHeadersDef, ctx);

                // All headers are optional
                final var finalRequestFields = requestFields.entrySet().stream()
                        .collect(Collectors.toMap(e -> e.getKey(), e -> new VFieldDeclaration(e.getValue().fieldName,
                                e.getValue().typeDeclaration, true)));

                requestHeaders.putAll(finalRequestFields);
            } catch (MsgPactSchemaParseError e) {
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
                Map<String, VFieldDeclaration> responseFields = ParseStructFields.parseStructFields(responsePath,
                        (Map<String, Object>) responseHeadersDef, ctx);

                // All headers are optional
                final var finalResponseFields = responseFields.entrySet().stream()
                        .collect(Collectors.toMap(e -> e.getKey(), e -> new VFieldDeclaration(e.getValue().fieldName,
                                e.getValue().typeDeclaration, true)));

                responseHeaders.putAll(finalResponseFields);
            } catch (MsgPactSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new MsgPactSchemaParseError(parseFailures, ctx.msgPactSchemaDocumentNamesToJson);
        }

        return new VHeaders(schemaKey, requestHeaders, responseHeaders);
    }
}
