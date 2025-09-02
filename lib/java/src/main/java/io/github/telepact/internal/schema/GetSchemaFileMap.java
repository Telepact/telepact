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

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;

import io.github.telepact.TelepactSchemaParseError;

public class GetSchemaFileMap {

    public static Map<String, String> getSchemaFileMap(String directory) {
        var finalJsonDocuments = new HashMap<String, String>();

        var schemaParseFailures = new java.util.ArrayList<SchemaParseFailure>();

        try {
            var paths = Files.walk(Paths.get(directory)).toArray(Path[]::new);
            for (Path path : paths) {
                if (!Files.isRegularFile(path)) {
                    continue;
                }
                String content = new String(Files.readAllBytes(path));
                String relativePath = Paths.get(directory).relativize(path).toString();
                finalJsonDocuments.put(relativePath, content);
                if (!path.toString().endsWith(".telepact.json")) {
                    schemaParseFailures.add(new SchemaParseFailure(relativePath, new java.util.ArrayList<>(), "FileNamePatternInvalid", Map.of("expected", "*.telepact.json")));
                }
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        if (!schemaParseFailures.isEmpty()) {
            throw new TelepactSchemaParseError(schemaParseFailures, finalJsonDocuments);
        }

        return finalJsonDocuments;
    }

}
