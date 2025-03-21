package io.github.telepact;

import static io.github.telepact.internal.schema.GetSchemaFileMap.getSchemaFileMap;

import java.util.Map;

public class TelepactSchemaFiles {

    public final Map<String, String> filenamesToJson;

    public TelepactSchemaFiles(String directory) {
        this.filenamesToJson = getSchemaFileMap(directory);
    }
}
