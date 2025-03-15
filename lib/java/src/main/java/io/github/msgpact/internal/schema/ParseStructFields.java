package io.github.msgpact.internal.schema;

import static io.github.msgpact.internal.schema.ParseField.parseField;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import io.github.msgpact.MsgPactSchemaParseError;
import io.github.msgpact.internal.types.VFieldDeclaration;

public class ParseStructFields {
    static Map<String, VFieldDeclaration> parseStructFields(
            List<Object> path,
            Map<String, Object> referenceStruct, ParseContext ctx) {
        final var parseFailures = new ArrayList<SchemaParseFailure>();
        final var fields = new HashMap<String, VFieldDeclaration>();

        for (final var structEntry : referenceStruct.entrySet()) {
            final var fieldDeclaration = structEntry.getKey();

            for (final var existingField : fields.keySet()) {
                final var existingFieldNoOpt = existingField.split("!")[0];
                final var fieldNoOpt = fieldDeclaration.split("!")[0];
                if (fieldNoOpt.equals(existingFieldNoOpt)) {
                    final List<Object> finalPath = new ArrayList<>(path);
                    finalPath.add(fieldDeclaration);

                    final List<Object> finalOtherPath = new ArrayList<>(path);
                    finalOtherPath.add(existingField);

                    final var finalOtherDocumentJson = ctx.msgPactSchemaDocumentNamesToJson.get(ctx.documentName);
                    final var finalOtherLocationPseudoJson = GetPathDocumentCoordinatesPseudoJson
                            .getPathDocumentCoordinatesPseudoJson(finalOtherPath, finalOtherDocumentJson);

                    parseFailures
                            .add(new SchemaParseFailure(ctx.documentName, finalPath, "PathCollision",
                                    Map.of("document", ctx.documentName, "path", finalOtherPath, "location",
                                            finalOtherLocationPseudoJson)));
                }
            }

            final var typeDeclarationValue = structEntry.getValue();

            final VFieldDeclaration parsedField;
            try {
                parsedField = parseField(path, fieldDeclaration,
                        typeDeclarationValue, ctx);
                final String fieldName = parsedField.fieldName;

                fields.put(fieldName, parsedField);
            } catch (MsgPactSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new MsgPactSchemaParseError(parseFailures, ctx.msgPactSchemaDocumentNamesToJson);
        }

        return fields;
    }
}
