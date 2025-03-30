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

package io.github.telepact;

import static io.github.telepact.internal.schema.CreateMockTelepactSchemaFromJsonDocuments.createMockTelepactSchemaFromFileJsonMap;
import static io.github.telepact.internal.schema.GetSchemaFileMap.getSchemaFileMap;

import java.util.List;
import java.util.Map;

import io.github.telepact.internal.types.TFieldDeclaration;
import io.github.telepact.internal.types.TType;

/**
 * A parsed telepact schema.
 */
public class MockTelepactSchema {

    /**
     * The original schema objects.
     */
    public final List<Object> original;

    /**
     * The parsed schema types.
     */
    public final Map<String, TType> parsed;

    /**
     * The parsed request headers.
     */
    public final Map<String, TFieldDeclaration> parsedRequestHeaders;

    /**
     * Parsed response headers from the schema.
     */
    public final Map<String, TFieldDeclaration> parsedResponseHeaders;

    /**
     * Constructs a MockTelepactSchema with the given original objects and parsed data.
     *
     * @param original the original list of objects
     * @param parsed the parsed map of TType objects
     * @param parsedRequestHeaders the parsed request headers
     * @param parsedResponseHeaders the parsed response headers
     */
    public MockTelepactSchema(List<Object> original,
            Map<String, TType> parsed,
            Map<String, TFieldDeclaration> parsedRequestHeaders,
            Map<String, TFieldDeclaration> parsedResponseHeaders) {
        this.original = original;
        this.parsed = parsed;
        this.parsedRequestHeaders = parsedRequestHeaders;
        this.parsedResponseHeaders = parsedResponseHeaders;
    }

    /**
     * Creates a MockTelepactSchema from a JSON string.
     *
     * @param json the JSON string
     * @return a MockTelepactSchema instance
     */
    public static MockTelepactSchema fromJson(String json) {
        return createMockTelepactSchemaFromFileJsonMap(Map.of("auto_", json));
    }

    /**
     * Creates a MockTelepactSchema from a map of file JSON strings.
     *
     * @param fileJsonMap the map of file names to JSON strings
     * @return a MockTelepactSchema instance
     */
    public static MockTelepactSchema fromFileJsonMap(Map<String, String> fileJsonMap) {
        return createMockTelepactSchemaFromFileJsonMap(fileJsonMap);
    }

    /**
     * Creates a MockTelepactSchema from a directory.
     *
     * @param directory the directory path
     * @return a MockTelepactSchema instance
     */
    public static MockTelepactSchema fromDirectory(String directory) {
        final var map = getSchemaFileMap(directory);
        return createMockTelepactSchemaFromFileJsonMap(map);
    }
}
