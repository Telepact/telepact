package uapi.internal.schema;

import static uapi.internal.schema.ParseField.parseField;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import uapi.UApiSchemaParseError;
import uapi.internal.types.UFieldDeclaration;
import uapi.internal.types.UType;

public class ParseStructFields {
    static Map<String, UFieldDeclaration> parseStructFields(Map<String, Object> referenceStruct, List<Object> path,
            int typeParameterCount, List<Object> uApiSchemaPseudoJson, Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes, Map<String, UType> typeExtensions,
            List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        final var parseFailures = new ArrayList<SchemaParseFailure>();
        final var fields = new HashMap<String, UFieldDeclaration>();

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

                    parseFailures
                            .add(new SchemaParseFailure(finalPath, "PathCollision",
                                    Map.of("other", finalOtherPath), null));
                }
            }

            final var typeDeclarationValue = structEntry.getValue();

            final UFieldDeclaration parsedField;
            try {
                parsedField = parseField(path, fieldDeclaration,
                        typeDeclarationValue, typeParameterCount, uApiSchemaPseudoJson, schemaKeysToIndex,
                        parsedTypes,
                        typeExtensions, allParseFailures, failedTypes);
                final String fieldName = parsedField.fieldName;

                fields.put(fieldName, parsedField);
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }

        return fields;
    }
}
