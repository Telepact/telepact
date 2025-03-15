package io.github.msgpact;

import static io.github.msgpact.internal.schema.GetSchemaFileMap.getSchemaFileMap;

import java.util.Map;

public class MsgPactSchemaFiles {

    public final Map<String, String> filenamesToJson;

    public MsgPactSchemaFiles(String directory) {
        this.filenamesToJson = getSchemaFileMap(directory);
    }
}
