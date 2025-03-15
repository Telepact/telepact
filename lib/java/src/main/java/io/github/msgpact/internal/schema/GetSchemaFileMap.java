package io.github.msgpact.internal.schema;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;

public class GetSchemaFileMap {

    public static Map<String, String> getSchemaFileMap(String directory) {
        var finalJsonDocuments = new HashMap<String, String>();

        try {
            var paths = Files.walk(Paths.get(directory)).toArray(Path[]::new);
            for (Path path : paths) {
                if (path.toString().endsWith(".msgpact.json")) {
                    String content = new String(Files.readAllBytes(path));
                    String relativePath = Paths.get(directory).relativize(path).toString();
                    finalJsonDocuments.put(relativePath, content);
                }
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        return finalJsonDocuments;
    }

}
