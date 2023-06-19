package io.github.brenbar.japi.server;

import io.github.brenbar.japi.BinaryEncoder;
import io.github.brenbar.japi.Parser;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Map;
import java.util.TreeSet;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;

class BuildBinaryEncoder {

    static BinaryEncoder build(Map<String, Parser.Definition> apiDescription) {
        var allApiDescriptionKeys = new TreeSet<String>();
        for (var entry : apiDescription.entrySet()) {
            allApiDescriptionKeys.add(entry.getKey());
            if (entry.getValue() instanceof Parser.FunctionDefinition f) {
                allApiDescriptionKeys.addAll(f.inputStruct().fields().keySet());
                allApiDescriptionKeys.addAll(f.outputStruct().fields().keySet());
                allApiDescriptionKeys.addAll(f.errors());
            } else if (entry.getValue() instanceof Parser.TypeDefinition t) {
                var type = t.type();
                if (type instanceof Parser.Struct o) {
                    allApiDescriptionKeys.addAll(o.fields().keySet());
                } else if (type instanceof Parser.Enum u) {
                    allApiDescriptionKeys.addAll(u.cases().keySet());
                }
            } else if (entry.getValue() instanceof Parser.ErrorDefinition e) {
                allApiDescriptionKeys.addAll(e.fields().keySet());
            }
        }
        var atomicLong = new AtomicLong(0);
        var binaryEncoding = allApiDescriptionKeys.stream().collect(Collectors.toMap(k -> k, k -> atomicLong.getAndIncrement()));
        var finalString = allApiDescriptionKeys.stream().collect(Collectors.joining("\n"));
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
