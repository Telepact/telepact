//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
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
