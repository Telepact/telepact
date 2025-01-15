package uapi;

import static uapi.internal.schema.GetSchemaFileMap.getSchemaFileMap;

import java.util.Map;

public class UApiSchemaFiles {

    public final Map<String, String> filenamesToJson;

    public UApiSchemaFiles(String directory) {
        this.filenamesToJson = getSchemaFileMap(directory);
    }
}
