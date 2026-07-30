//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.schema;

import static io.github.telepact.internal.schema.GetPathDocumentCoordinatesPseudoJson.getPathDocumentCoordinatesPseudoJson;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class DocumentLocators {
    @FunctionalInterface
    public interface DocumentLocator {
        Map<String, Object> locate(List<Object> path);
    }

    public static class SchemaDocumentMap extends HashMap<String, String> {
        public final Map<String, DocumentLocator> documentLocators = new HashMap<>();

        public SchemaDocumentMap() {
            super();
        }

        public SchemaDocumentMap(Map<String, String> other) {
            super(other);
            if (other instanceof SchemaDocumentMap schemaDocumentMap) {
                this.documentLocators.putAll(schemaDocumentMap.documentLocators);
            }
        }
    }

    public static SchemaDocumentMap copyDocumentLocators(Map<String, String> source, Map<String, String> destination) {
        final var mapped = destination instanceof SchemaDocumentMap schemaDocumentMap
                ? schemaDocumentMap
                : new SchemaDocumentMap(destination);
        if (source instanceof SchemaDocumentMap schemaSource) {
            mapped.documentLocators.putAll(schemaSource.documentLocators);
        }
        return mapped;
    }

    public static Map<String, Object> resolveDocumentCoordinates(
            List<Object> path,
            String documentName,
            Map<String, String> documentNamesToJson) {
        if (documentNamesToJson instanceof SchemaDocumentMap schemaDocumentMap) {
            final var locator = schemaDocumentMap.documentLocators.get(documentName);
            if (locator != null) {
                return locator.locate(path);
            }
        }
        return getPathDocumentCoordinatesPseudoJson(path, documentNamesToJson.get(documentName));
    }
}
