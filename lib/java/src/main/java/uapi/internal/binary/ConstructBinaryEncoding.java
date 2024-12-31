package uapi.internal.binary;

import static uapi.internal.binary.CreateChecksum.createChecksum;

import java.util.Map;
import java.util.TreeMap;
import java.util.TreeSet;

import uapi.UApiSchema;
import uapi.internal.types.UFieldDeclaration;
import uapi.internal.types.UFn;
import uapi.internal.types.UStruct;
import uapi.internal.types.UUnion;

public class ConstructBinaryEncoding {
    public static BinaryEncoding constructBinaryEncoding(UApiSchema uApiSchema) {
        final var allKeys = new TreeSet<String>();
        for (final var entry : uApiSchema.parsed.entrySet()) {
            allKeys.add(entry.getKey());

            if (entry.getValue() instanceof final UStruct s) {
                final Map<String, UFieldDeclaration> structFields = s.fields;
                allKeys.addAll(structFields.keySet());
            } else if (entry.getValue() instanceof final UUnion u) {
                final Map<String, UStruct> unionCases = u.cases;
                for (final var entry2 : unionCases.entrySet()) {
                    allKeys.add(entry2.getKey());
                    final var struct = entry2.getValue();
                    final var structFields = struct.fields;
                    allKeys.addAll(structFields.keySet());
                }
            } else if (entry.getValue() instanceof final UFn f) {
                final UUnion fnCall = f.call;
                final Map<String, UStruct> fnCallCases = fnCall.cases;
                final UUnion fnResult = f.result;
                final Map<String, UStruct> fnResultCases = fnResult.cases;

                for (final var e2 : fnCallCases.entrySet()) {
                    allKeys.add(e2.getKey());
                    final var struct = e2.getValue();
                    final Map<String, UFieldDeclaration> structFields = struct.fields;
                    allKeys.addAll(structFields.keySet());
                }

                for (var e2 : fnResultCases.entrySet()) {
                    allKeys.add(e2.getKey());
                    var struct = e2.getValue();
                    final Map<String, UFieldDeclaration> structFields = struct.fields;
                    allKeys.addAll(structFields.keySet());
                }
            }
        }
        var i = 0;
        final var binaryEncodingMap = new TreeMap<String, Integer>();
        for (final var key : allKeys) {
            binaryEncodingMap.put(key, i);
            i += 1;
        }
        final var finalString = String.join("\n", allKeys);
        final int checksum = createChecksum(finalString);
        return new BinaryEncoding(binaryEncodingMap, checksum);
    }
}
