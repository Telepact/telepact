package uapi.internal.schema;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import uapi.UApiSchemaParseError;

import static uapi.internal.schema.GetPathDocumentCoordinatesPseudoJson.getPathDocumentCoordinatesPseudoJson;

public class CatchHeaderCollisions {

    public static void catchHeaderCollisions(
            Map<String, List<Object>> uApiSchemaNameToPseudoJson,
            Set<String> headerKeys,
            Map<String, Integer> keysToIndex,
            Map<String, String> schemaKeysToDocumentNames,
            Map<String, String> documentNamesToJson) {
        List<SchemaParseFailure> parseFailures = new ArrayList<>();

        List<String> headerKeysList = new ArrayList<>(headerKeys);

        headerKeysList.sort((k1, k2) -> {
            String documentName1 = schemaKeysToDocumentNames.get(k1);
            String documentName2 = schemaKeysToDocumentNames.get(k2);
            if (!documentName1.equals(documentName2)) {
                return documentName1.compareTo(documentName2);
            } else {
                int index1 = keysToIndex.get(k1);
                int index2 = keysToIndex.get(k2);
                return Integer.compare(index1, index2);
            }
        });

        for (int i = 0; i < headerKeysList.size(); i++) {
            for (int j = i + 1; j < headerKeysList.size(); j++) {
                String defKey = headerKeysList.get(i);
                String otherDefKey = headerKeysList.get(j);

                int index = keysToIndex.get(defKey);
                int otherIndex = keysToIndex.get(otherDefKey);

                String documentName = schemaKeysToDocumentNames.get(defKey);
                String otherDocumentName = schemaKeysToDocumentNames.get(otherDefKey);

                List<Object> uApiSchemaPseudoJson = uApiSchemaNameToPseudoJson.get(documentName);
                List<Object> otherUApiSchemaPseudoJson = uApiSchemaNameToPseudoJson.get(otherDocumentName);

                Map<String, Object> def = (Map<String, Object>) uApiSchemaPseudoJson.get(index);
                Map<String, Object> otherDef = (Map<String, Object>) otherUApiSchemaPseudoJson.get(otherIndex);

                Map<String, Object> headerDef = (Map<String, Object>) def.get(defKey);
                Map<String, Object> otherHeaderDef = (Map<String, Object>) otherDef.get(otherDefKey);

                Set<String> headerCollisions = new HashSet<>(headerDef.keySet());
                headerCollisions.retainAll(otherHeaderDef.keySet());
                for (String headerCollision : headerCollisions) {
                    List<Object> thisPath = Arrays.asList(index, defKey, headerCollision);
                    String thisDocumentJson = documentNamesToJson.get(documentName);
                    Object thisLocation = getPathDocumentCoordinatesPseudoJson(thisPath, thisDocumentJson);
                    parseFailures.add(new SchemaParseFailure(
                            otherDocumentName,
                            Arrays.asList(otherIndex, otherDefKey, headerCollision),
                            "PathCollision",
                            Map.of("document", documentName, "path", thisPath, "location", thisLocation)));
                }

                Map<String, Object> resHeaderDef = (Map<String, Object>) def.get("->");
                Map<String, Object> otherResHeaderDef = (Map<String, Object>) otherDef.get("->");

                Set<String> resHeaderCollisions = new HashSet<>(resHeaderDef.keySet());
                resHeaderCollisions.retainAll(otherResHeaderDef.keySet());
                for (String resHeaderCollision : resHeaderCollisions) {
                    List<Object> thisPath = Arrays.asList(index, "->", resHeaderCollision);
                    String thisDocumentJson = documentNamesToJson.get(documentName);
                    Object thisLocation = getPathDocumentCoordinatesPseudoJson(thisPath, thisDocumentJson);
                    parseFailures.add(new SchemaParseFailure(
                            otherDocumentName,
                            Arrays.asList(otherIndex, "->", resHeaderCollision),
                            "PathCollision",
                            Map.of("document", documentName, "path", thisPath, "location", thisLocation)));
                }
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures, documentNamesToJson);
        }
    }
}