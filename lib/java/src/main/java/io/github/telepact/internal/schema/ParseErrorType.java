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

import static io.github.telepact.internal.schema.ParseUnionType.parseUnionType;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import io.github.telepact.TelepactSchemaParseError;
import io.github.telepact.internal.types.VError;
import io.github.telepact.internal.types.VUnion;

public class ParseErrorType {
    public static VError parseErrorType(
            List<Object> path,
            Map<String, Object> errorDefinitionAsParsedJson,
            String schemaKey,
            ParseContext ctx) {

        List<SchemaParseFailure> parseFailures = new ArrayList<>();

        Set<String> otherKeys = new HashSet<>(errorDefinitionAsParsedJson.keySet());
        otherKeys.remove(schemaKey);
        otherKeys.remove("///");

        if (!otherKeys.isEmpty()) {
            for (String k : otherKeys) {
                List<Object> loopPath = new ArrayList<>(path);
                loopPath.add(k);
                parseFailures
                        .add(new SchemaParseFailure(ctx.documentName, loopPath, "ObjectKeyDisallowed",
                                new HashMap<>()));
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new TelepactSchemaParseError(parseFailures, ctx.telepactSchemaDocumentNamesToJson);
        }

        // Assuming parseUnionType is adapted to Java and returns UError or its

        VUnion error = parseUnionType(path, errorDefinitionAsParsedJson, schemaKey,
                new ArrayList<>(),
                new ArrayList<>(), ctx);

        return new VError(schemaKey, error);
    }
}
