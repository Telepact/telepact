//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.schema;

import static io.github.telepact.internal.schema.CreateTelepactSchemaFromFileJsonMap.createTelepactSchemaFromFileJsonMap;
import static io.github.telepact.internal.schema.GetMockTelepactJson.getMockTelepactJson;

import java.util.Map;

import io.github.telepact.MockTelepactSchema;
import io.github.telepact.internal.schema.DocumentLocators.SchemaDocumentMap;

public class CreateMockTelepactSchemaFromJsonDocuments {
    public static MockTelepactSchema createMockTelepactSchemaFromFileJsonMap(Map<String, String> jsonDocuments) {
        var finalJsonDocuments = new SchemaDocumentMap(jsonDocuments);
        finalJsonDocuments.put("mock_", getMockTelepactJson());

        var telepactSchema = createTelepactSchemaFromFileJsonMap(finalJsonDocuments);

        return new MockTelepactSchema(telepactSchema.original, telepactSchema.full, telepactSchema.parsed, telepactSchema.parsedRequestHeaders,
                telepactSchema.parsedResponseHeaders);
    }
}
