package io.github.brenbar.japi.server;

import io.github.brenbar.japi.BinaryEncoder;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HashMap;
import java.util.Map;
import java.util.TreeSet;

class BuildBinaryEncoder {

    static BinaryEncoder build(Map<String, Definition> definitions) {
        var allKeys = new TreeSet<String>();
        for (var entry : definitions.entrySet()) {
            allKeys.add(entry.getKey());
            if (entry.getValue() instanceof FunctionDefinition f) {
                allKeys.addAll(f.inputStruct().fields().keySet());
                allKeys.addAll(f.outputStruct().fields().keySet());
                allKeys.addAll(f.errors());
            } else if (entry.getValue() instanceof TypeDefinition t) {
                var type = t.type();
                if (type instanceof Struct o) {
                    allKeys.addAll(o.fields().keySet());
                } else if (type instanceof Enum u) {
                    allKeys.addAll(u.cases().keySet());
                }
            } else if (entry.getValue() instanceof ErrorDefinition e) {
                allKeys.addAll(e.fields().keySet());
            }
        }
        var i = (long) 0;
        var binaryEncoding = new HashMap<String, Long>();
        for (var key : allKeys) {
            binaryEncoding.put(key, i++);
        }
        var finalString = String.join("\n", allKeys);
        long binaryHash;
        try {
            var hash = MessageDigest.getInstance("SHA-256").digest(finalString.getBytes(StandardCharsets.UTF_8));
            var buffer = ByteBuffer.wrap(hash);
            binaryHash = buffer.getLong();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
        return new BinaryEncoder(binaryEncoding, binaryHash);
    }
}
