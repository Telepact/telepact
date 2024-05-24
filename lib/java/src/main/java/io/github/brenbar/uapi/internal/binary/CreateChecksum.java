package io.github.brenbar.uapi.internal.binary;

import java.nio.charset.StandardCharsets;
import java.util.zip.CRC32;

public class CreateChecksum {
    static int createChecksum(String value) {
        var c = new CRC32();
        c.update(value.getBytes(StandardCharsets.UTF_8));
        return (int) c.getValue();
    }
}
