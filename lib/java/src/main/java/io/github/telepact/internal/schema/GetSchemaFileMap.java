//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.schema;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Map;

import io.github.telepact.TelepactSchemaParseError;
import io.github.telepact.internal.schema.DocumentLocators.SchemaDocumentMap;

public class GetSchemaFileMap {

    public static Map<String, String> getSchemaFileMap(String directory) {
        var finalJsonDocuments = new SchemaDocumentMap();

        var schemaParseFailures = new java.util.ArrayList<SchemaParseFailure>();

        try {
            var paths = Files.list(Paths.get(directory))
                    .sorted()
                    .toArray(Path[]::new);
            for (Path path : paths) {
                String relativePath = Paths.get(directory).relativize(path).toString();
                if (!Files.isRegularFile(path)) {
                    schemaParseFailures.add(new SchemaParseFailure(relativePath, new java.util.ArrayList<>(), "DirectoryDisallowed", Map.of()));
                    finalJsonDocuments.put(relativePath, "[]");
                    continue;
                }
                String content = new String(Files.readAllBytes(path));
                if (path.toString().endsWith(".telepact.json")) {
                    finalJsonDocuments.put(relativePath, content);
                } else if (path.toString().endsWith(".telepact.yaml")) {
                    try {
                        var parsed = ParseTelepactYaml.parseTelepactYaml(content);
                        finalJsonDocuments.put(relativePath, parsed.canonicalJson);
                        if (parsed.locator != null) {
                            finalJsonDocuments.documentLocators.put(relativePath, parsed.locator);
                        }
                    } catch (Exception e) {
                        finalJsonDocuments.put(relativePath, "[]");
                        schemaParseFailures.add(new SchemaParseFailure(relativePath, new java.util.ArrayList<>(), "JsonInvalid", Map.of()));
                    }
                } else {
                    finalJsonDocuments.put(relativePath, content);
                    schemaParseFailures.add(new SchemaParseFailure(relativePath, new java.util.ArrayList<>(), "FileNamePatternInvalid", Map.of("expected", "*.telepact.json|*.telepact.yaml")));
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
