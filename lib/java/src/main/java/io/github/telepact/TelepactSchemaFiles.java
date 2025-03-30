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

import static io.github.telepact.internal.schema.GetSchemaFileMap.getSchemaFileMap;

import java.util.Map;

/**
 * Represents a collection of schema files.
 */
public class TelepactSchemaFiles {
    /**
     * A map of file names to their corresponding JSON content.
     */
    public final Map<String, String> filenamesToJson;

    /**
     * Constructs a new TelepactSchemaFiles object for the specified directory.
     *
     * @param directory the directory containing the schema files
     */
    public TelepactSchemaFiles(String directory) {
        this.filenamesToJson = getSchemaFileMap(directory);
    }
}
