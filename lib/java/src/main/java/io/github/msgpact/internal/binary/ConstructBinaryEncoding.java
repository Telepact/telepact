package io.github.msgpact.internal.binary;

import static io.github.msgpact.internal.binary.CreateChecksum.createChecksum;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.TreeSet;

import io.github.msgpact.MsgPactSchema;
import io.github.msgpact.internal.types.VArray;
import io.github.msgpact.internal.types.VFn;
import io.github.msgpact.internal.types.VObject;
import io.github.msgpact.internal.types.VStruct;
import io.github.msgpact.internal.types.VTypeDeclaration;
import io.github.msgpact.internal.types.VUnion;

public class ConstructBinaryEncoding {

    private static List<String> traceType(VTypeDeclaration typeDeclaration) {
        final var thisAllKeys = new ArrayList<String>();

        if (typeDeclaration.type instanceof VArray) {
            final var theseKeys2 = traceType(typeDeclaration.typeParameters.get(0));
            thisAllKeys.addAll(theseKeys2);
        } else if (typeDeclaration.type instanceof VObject) {
            final var theseKeys2 = traceType(typeDeclaration.typeParameters.get(0));
            thisAllKeys.addAll(theseKeys2);
        } else if (typeDeclaration.type instanceof VStruct s) {
            final var structFields = s.fields;
            for (final var entry : structFields.entrySet()) {
                final var structFieldKey = entry.getKey();
                final var structField = entry.getValue();
                thisAllKeys.add(structFieldKey);
                final var moreKeys = traceType(structField.typeDeclaration);
                thisAllKeys.addAll(moreKeys);
            }
        } else if (typeDeclaration.type instanceof VUnion u) {
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

    public static BinaryEncoding constructBinaryEncoding(MsgPactSchema msgPactSchema) {
        final var allKeys = new TreeSet<String>();
        final var functions = new ArrayList<Map.Entry<String, VFn>>();

        for (final var entry : msgPactSchema.parsed.entrySet()) {
            final var key = entry.getKey();
            final var value = entry.getValue();
            if (value instanceof VFn) {
                functions.add(Map.entry(key, (VFn) value));
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