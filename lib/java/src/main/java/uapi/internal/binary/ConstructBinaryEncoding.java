package uapi.internal.binary;

import static uapi.internal.binary.CreateChecksum.createChecksum;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.TreeSet;

import uapi.UApiSchema;
import uapi.internal.types.UArray;
import uapi.internal.types.UFn;
import uapi.internal.types.UObject;
import uapi.internal.types.UStruct;
import uapi.internal.types.UTypeDeclaration;
import uapi.internal.types.UUnion;

public class ConstructBinaryEncoding {

    private static List<String> traceType(UTypeDeclaration typeDeclaration) {
        final var thisAllKeys = new ArrayList<String>();

        if (typeDeclaration.type instanceof UArray) {
            final var theseKeys2 = traceType(typeDeclaration.typeParameters.get(0));
            thisAllKeys.addAll(theseKeys2);
        } else if (typeDeclaration.type instanceof UObject) {
            final var theseKeys2 = traceType(typeDeclaration.typeParameters.get(0));
            thisAllKeys.addAll(theseKeys2);
        } else if (typeDeclaration.type instanceof UStruct s) {
            final var structFields = s.fields;
            for (final var entry : structFields.entrySet()) {
                final var structFieldKey = entry.getKey();
                final var structField = entry.getValue();
                thisAllKeys.add(structFieldKey);
                final var moreKeys = traceType(structField.typeDeclaration);
                thisAllKeys.addAll(moreKeys);
            }
        } else if (typeDeclaration.type instanceof UUnion u) {
            final var unionTags = u.tags;
            for (final var entry : unionTags.entrySet()) {
                final var tagKey = entry.getKey();
                final var tagValue = entry.getValue();
                thisAllKeys.add(tagKey);
                final var structFields = tagValue.fields;
                for (final var fieldEntry : structFields.entrySet()) {
                    final var structFieldKey = fieldEntry.getKey();
                    final var structField = fieldEntry.getValue();
                    thisAllKeys.add(structFieldKey);
                    final var moreKeys = traceType(structField.typeDeclaration);
                    thisAllKeys.addAll(moreKeys);
                }
            }
        }

        return thisAllKeys;
    }

    public static BinaryEncoding constructBinaryEncoding(UApiSchema uApiSchema) {
        final var allKeys = new TreeSet<String>();
        final var functions = new ArrayList<Map.Entry<String, UFn>>();

        for (final var entry : uApiSchema.parsed.entrySet()) {
            final var key = entry.getKey();
            final var value = entry.getValue();
            if (value instanceof UFn) {
                functions.add(Map.entry(key, (UFn) value));
            }
        }

        for (final var function : functions) {
            final var key = function.getKey();
            final var value = function.getValue();
            allKeys.add(key);
            final var args = value.call.tags.get(key);
            for (final var fieldEntry : args.fields.entrySet()) {
                final var fieldKey = fieldEntry.getKey();
                final var field = fieldEntry.getValue();
                allKeys.add(fieldKey);
                final var keys = traceType(field.typeDeclaration);
                keys.forEach(allKeys::add);
            }

            final var result = value.result.tags.get("Ok_");
            allKeys.add("Ok_");
            for (final var fieldEntry : result.fields.entrySet()) {
                final var fieldKey = fieldEntry.getKey();
                final var field = fieldEntry.getValue();
                allKeys.add(fieldKey);
                final var keys = traceType(field.typeDeclaration);
                keys.forEach(allKeys::add);
            }
        }

        final var sortedAllKeys = new ArrayList<>(allKeys);
        Collections.sort(sortedAllKeys);

        final var binaryEncoding = new HashMap<String, Integer>();
        for (int index = 0; index < sortedAllKeys.size(); index++) {
            final var key = sortedAllKeys.get(index);
            binaryEncoding.put(key, index);
        }

        final var finalString = String.join("\n", sortedAllKeys);
        final var checksum = createChecksum(finalString);

        return new BinaryEncoding(binaryEncoding, checksum);
    }
}