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

import static io.github.telepact.internal.schema.ParseStructFields.parseStructFields;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import io.github.telepact.TelepactSchemaParseError;
import io.github.telepact.internal.types.VFieldDeclaration;
import io.github.telepact.internal.types.VHeaders;

public class ParseHeadersType {

    public static VHeaders parseHeadersType(
            List<Object> path,
            Map<String, Object> headersDefinitionAsParsedJson,
            String schemaKey,
            ParseContext ctx) throws TelepactSchemaParseError {
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
            } catch (TelepactSchemaParseError e) {
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
            } catch (TelepactSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new TelepactSchemaParseError(parseFailures, ctx.telepactSchemaDocumentNamesToJson);
        }

        return new VHeaders(schemaKey, requestHeaders, responseHeaders);
    }
}
