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

import static io.github.telepact.internal.schema.CreateTelepactSchemaFromFileJsonMap.createTelepactSchemaFromFileJsonMap;
import static io.github.telepact.internal.schema.GetSchemaFileMap.getSchemaFileMap;

import java.util.List;
import java.util.Map;

import io.github.telepact.internal.types.TFieldDeclaration;
import io.github.telepact.internal.types.TType;

/**
 * A parsed telepact schema.
 */
public class TelepactSchema {

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
     * The parsed response headers.
     */
    public final Map<String, TFieldDeclaration> parsedResponseHeaders;

    /**
     * Constructs a new TelepactSchema with the specified parameters.
     *
     * @param original the original schema objects
     * @param parsed the parsed schema types
     * @param parsedRequestHeaders the parsed request headers
     * @param parsedResponseHeaders the parsed response headers
     */
    public TelepactSchema(List<Object> original,
            Map<String, TType> parsed,
            Map<String, TFieldDeclaration> parsedRequestHeaders,
            Map<String, TFieldDeclaration> parsedResponseHeaders) {
        this.original = original;
        this.parsed = parsed;
        this.parsedRequestHeaders = parsedRequestHeaders;
        this.parsedResponseHeaders = parsedResponseHeaders;
    }

    /**
     * Creates a TelepactSchema from a JSON string.
     *
     * @param json the JSON string
     * @return the created TelepactSchema
     */
    public static TelepactSchema fromJson(String json) {
        return createTelepactSchemaFromFileJsonMap(Map.of("auto_", json));
    }

    /**
     * Creates a TelepactSchema from a map of file names to JSON strings.
     *
     * @param fileJsonMap the map of file names to JSON strings
     * @return the created TelepactSchema
     */
    public static TelepactSchema fromFileJsonMap(Map<String, String> fileJsonMap) {
        return createTelepactSchemaFromFileJsonMap(fileJsonMap);
    }

    /**
     * Creates a TelepactSchema from a directory.
     *
     * @param directory the directory path
     * @return the created TelepactSchema
     */
    public static TelepactSchema fromDirectory(String directory) {
        final var map = getSchemaFileMap(directory);
        return createTelepactSchemaFromFileJsonMap(map);
    }
}
