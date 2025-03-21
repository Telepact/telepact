//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

package io.github.telepact.internal.schema;

import java.util.List;
import java.util.Map;
import java.util.Set;

import io.github.telepact.internal.types.VType;

public class ParseContext {

    public final String documentName;
    public final Map<String, List<Object>> telepactSchemaDocumentsToPseudoJson;
    public final Map<String, String> telepactSchemaDocumentNamesToJson;
    public final Map<String, String> schemaKeysToDocumentName;
    public final Map<String, Integer> schemaKeysToIndex;
    public final Map<String, VType> parsedTypes;
    public final List<SchemaParseFailure> allParseFailures;
    public final Set<String> failedTypes;

    public ParseContext(String documentName,
            Map<String, List<Object>> telepactSchemaDocumentsToPseudoJson,
            Map<String, String> telepactSchemaDocumentNamesToJson,
            Map<String, String> schemaKeysToDocumentName, Map<String, Integer> schemaKeysToIndex,
            Map<String, VType> parsedTypes,
            List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        this.documentName = documentName;
        this.telepactSchemaDocumentsToPseudoJson = telepactSchemaDocumentsToPseudoJson;
        this.telepactSchemaDocumentNamesToJson = telepactSchemaDocumentNamesToJson;
        this.schemaKeysToDocumentName = schemaKeysToDocumentName;
        this.schemaKeysToIndex = schemaKeysToIndex;
        this.parsedTypes = parsedTypes;
        this.allParseFailures = allParseFailures;
        this.failedTypes = failedTypes;
    }

    public ParseContext copyWithNewDocumentName(String documentName) {
        return new ParseContext(documentName, telepactSchemaDocumentsToPseudoJson, telepactSchemaDocumentNamesToJson,
                schemaKeysToDocumentName,
                schemaKeysToIndex, parsedTypes, allParseFailures, failedTypes);
    }
}
