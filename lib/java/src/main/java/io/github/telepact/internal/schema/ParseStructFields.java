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

import static io.github.telepact.internal.schema.ParseField.parseField;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import io.github.telepact.TelepactSchemaParseError;
import io.github.telepact.internal.types.TFieldDeclaration;

public class ParseStructFields {
    static Map<String, TFieldDeclaration> parseStructFields(
            List<Object> path,
            Map<String, Object> referenceStruct, 
            boolean isHeader, ParseContext ctx) {
        final var parseFailures = new ArrayList<SchemaParseFailure>();
        final var fields = new HashMap<String, TFieldDeclaration>();

        for (final var structEntry : referenceStruct.entrySet()) {
            final var fieldDeclaration = structEntry.getKey();

        for (final var existingField : fields.keySet()) {
        final var existingFieldNoOpt = existingField.split("!")[0];
        final var fieldNoOpt = fieldDeclaration.split("!")[0];
        if (fieldNoOpt.equals(existingFieldNoOpt)) {
            final List<Object> structPath = new ArrayList<>(path);
            parseFailures
                .add(new SchemaParseFailure(ctx.documentName, structPath, "DuplicateField",
                    Map.of("field", fieldNoOpt)));
        }
        }

            final var typeDeclarationValue = structEntry.getValue();

            final TFieldDeclaration parsedField;
            try {
                parsedField = parseField(path, fieldDeclaration,
                        typeDeclarationValue, isHeader, ctx);
                final String fieldName = parsedField.fieldName;

                fields.put(fieldName, parsedField);
            } catch (TelepactSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new TelepactSchemaParseError(parseFailures, ctx.telepactSchemaDocumentNamesToJson);
        }

        return fields;
    }
}
