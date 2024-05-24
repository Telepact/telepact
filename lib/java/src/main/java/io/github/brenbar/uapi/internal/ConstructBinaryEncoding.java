package io.github.brenbar.uapi.internal;

import java.util.HashMap;
import java.util.Map;
import java.util.TreeSet;

import io.github.brenbar.uapi.UApiSchema;

import static io.github.brenbar.uapi.internal.CreateChecksum.createChecksum;

public class ConstructBinaryEncoding {
    public static _BinaryEncoding constructBinaryEncoding(UApiSchema uApiSchema) {
        final var allKeys = new TreeSet<String>();
        for (final var entry : uApiSchema.parsed.entrySet()) {
            allKeys.add(entry.getKey());

            if (entry.getValue() instanceof final _UStruct s) {
                final Map<String, _UFieldDeclaration> structFields = s.fields;
                allKeys.addAll(structFields.keySet());
            } else if (entry.getValue() instanceof final _UUnion u) {
                final Map<String, _UStruct> unionCases = u.cases;
                for (final var entry2 : unionCases.entrySet()) {
                    allKeys.add(entry2.getKey());
                    final var struct = entry2.getValue();
                    final var structFields = struct.fields;
                    allKeys.addAll(structFields.keySet());
                }
            } else if (entry.getValue() instanceof final _UFn f) {
                final _UUnion fnCall = f.call;
                final Map<String, _UStruct> fnCallCases = fnCall.cases;
                final _UUnion fnResult = f.result;
                final Map<String, _UStruct> fnResultCases = fnResult.cases;

                for (final var e2 : fnCallCases.entrySet()) {
                    allKeys.add(e2.getKey());
                    final var struct = e2.getValue();
                    final Map<String, _UFieldDeclaration> structFields = struct.fields;
                    allKeys.addAll(structFields.keySet());
                }

                for (var e2 : fnResultCases.entrySet()) {
                    allKeys.add(e2.getKey());
                    var struct = e2.getValue();
                    final Map<String, _UFieldDeclaration> structFields = struct.fields;
                    allKeys.addAll(structFields.keySet());
                }
            }
        }
        var i = 0;
        final var binaryEncodingMap = new HashMap<String, Integer>();
        for (final var key : allKeys) {
            binaryEncodingMap.put(key, i);
            i += 1;
        }
        final var finalString = String.join("\n", allKeys);

        final int checksum = createChecksum(finalString);
        return new _BinaryEncoding(binaryEncodingMap, checksum);
    }
}
