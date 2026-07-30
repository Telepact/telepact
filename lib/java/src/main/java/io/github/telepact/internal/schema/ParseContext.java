//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.schema;

import java.util.List;
import java.util.Map;
import java.util.Set;

import io.github.telepact.internal.types.TType;

public class ParseContext {

    public final String documentName;
    public final Map<String, List<Object>> telepactSchemaDocumentsToPseudoJson;
    public final Map<String, String> telepactSchemaDocumentNamesToJson;
    public final Map<String, String> schemaKeysToDocumentName;
    public final Map<String, Integer> schemaKeysToIndex;
    public final Map<String, TType> parsedTypes;
    public final Map<String, String> fnErrorRegexes;
    public final List<SchemaParseFailure> allParseFailures;
    public final Set<String> failedTypes;

    public ParseContext(String documentName,
            Map<String, List<Object>> telepactSchemaDocumentsToPseudoJson,
            Map<String, String> telepactSchemaDocumentNamesToJson,
            Map<String, String> schemaKeysToDocumentName, Map<String, Integer> schemaKeysToIndex,
            Map<String, TType> parsedTypes,
            Map<String, String> fnErrorRegexes,
            List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        this.documentName = documentName;
        this.telepactSchemaDocumentsToPseudoJson = telepactSchemaDocumentsToPseudoJson;
        this.telepactSchemaDocumentNamesToJson = telepactSchemaDocumentNamesToJson;
        this.schemaKeysToDocumentName = schemaKeysToDocumentName;
        this.schemaKeysToIndex = schemaKeysToIndex;
        this.parsedTypes = parsedTypes;
        this.fnErrorRegexes = fnErrorRegexes;
        this.allParseFailures = allParseFailures;
        this.failedTypes = failedTypes;
    }

    public ParseContext copyWithNewDocumentName(String documentName) {
        return new ParseContext(documentName, telepactSchemaDocumentsToPseudoJson, telepactSchemaDocumentNamesToJson,
                schemaKeysToDocumentName,
                schemaKeysToIndex, parsedTypes, fnErrorRegexes, allParseFailures, failedTypes);
    }
}
