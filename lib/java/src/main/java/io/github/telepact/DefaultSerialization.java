//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

package io.github.telepact;

import java.io.IOException;
import java.io.ByteArrayOutputStream;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

import org.msgpack.core.MessagePack;
import org.msgpack.core.MessagePacker;
import org.msgpack.core.MessageUnpacker;
import org.msgpack.value.ValueType;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.github.telepact.internal.binary.BinaryEncoding;
import io.github.telepact.internal.binary.BinaryEncodingMissing;
import io.github.telepact.internal.binary.BinaryMsgPackSerialization;

class DefaultSerialization implements Serialization, BinaryMsgPackSerialization {

    private ObjectMapper jsonMapper = new ObjectMapper();

    @Override
    public byte[] toJson(Object telepactMessage) throws Throwable {
        return jsonMapper.writeValueAsBytes(telepactMessage);
    }

    public byte[] toMsgPack(Object telepactMessage) throws Throwable {
        final var out = new ByteArrayOutputStream();
        try (final var packer = MessagePack.newDefaultPacker(out)) {
            packMsgPackValue(packer, telepactMessage);
        }
        return out.toByteArray();
    }

    @Override
    public Object fromJson(byte[] bytes) throws Throwable {
        return jsonMapper.readValue(bytes, new TypeReference<Object>() {
        });
    }

    @Override
    public Object fromMsgPack(byte[] bytes) throws Throwable {
        try (final var unpacker = MessagePack.newDefaultUnpacker(bytes)) {
            return unpackMsgPackValue(unpacker);
        }
    }

    @Override
    public byte[] toBinaryMsgPack(Map<String, Object> headers, Map<String, Object> body,
            BinaryEncoding binaryEncoding) throws Throwable {
        final var out = new ByteArrayOutputStream();
        try (final var packer = MessagePack.newDefaultPacker(out)) {
            packer.packArrayHeader(2);
            packMsgPackValue(packer, headers);
            packBinaryMsgPackValue(packer, body, binaryEncoding);
        }
        return out.toByteArray();
    }

    @Override
    public MsgPackHeaders fromMsgPackHeaders(byte[] bytes) throws Throwable {
        try (final var unpacker = MessagePack.newDefaultUnpacker(bytes)) {
            if (unpacker.unpackArrayHeader() != 2) {
                throw new IOException("expected Telepact msgpack message array");
            }
            final var headers = toStringMap(unpackMsgPackValue(unpacker));
            return new MsgPackHeaders(headers, (int) unpacker.getTotalReadBytes());
        }
    }

    @Override
    public Map<String, Object> fromMsgPackBody(byte[] bytes, int offset, BinaryEncoding binaryEncoding) throws Throwable {
        try (final var unpacker = MessagePack.newDefaultUnpacker(bytes, offset, bytes.length - offset)) {
            return (Map<String, Object>) unpackBinaryMsgPackValue(unpacker, binaryEncoding);
        }
    }

    private static void packMsgPackValue(MessagePacker packer, Object value) throws IOException {
        if (value == null) {
            packer.packNil();
        } else if (value instanceof String s) {
            packer.packString(s);
        } else if (value instanceof Boolean b) {
            packer.packBoolean(b);
        } else if (value instanceof Byte b) {
            packer.packByte(b);
        } else if (value instanceof Short s) {
            packer.packShort(s);
        } else if (value instanceof Integer i) {
            packer.packInt(i);
        } else if (value instanceof Long l) {
            packer.packLong(l);
        } else if (value instanceof BigInteger b) {
            packer.packBigInteger(b);
        } else if (value instanceof Float f) {
            packer.packDouble(f.doubleValue());
        } else if (value instanceof Double d) {
            packer.packDouble(d);
        } else if (value instanceof byte[] bytes) {
            packer.packBinaryHeader(bytes.length);
            packer.writePayload(bytes);
        } else if (value instanceof List<?> list) {
            packer.packArrayHeader(list.size());
            for (final var item : list) {
                packMsgPackValue(packer, item);
            }
        } else if (value instanceof Map<?, ?> map) {
            packer.packMapHeader(map.size());
            for (final var entry : map.entrySet()) {
                packMsgPackValue(packer, entry.getKey());
                packMsgPackValue(packer, entry.getValue());
            }
        } else {
            throw new IOException("unsupported msgpack value type: " + value.getClass().getName());
        }
    }

    private static Object unpackMsgPackValue(MessageUnpacker unpacker) throws IOException {
        final var format = unpacker.getNextFormat();
        final ValueType type = format.getValueType();
        if (type == ValueType.NIL) {
            unpacker.unpackNil();
            return null;
        }
        if (type == ValueType.BOOLEAN) {
            return unpacker.unpackBoolean();
        }
        if (type == ValueType.INTEGER) {
            return narrowInteger(unpacker.unpackBigInteger());
        }
        if (type == ValueType.FLOAT) {
            return unpacker.unpackDouble();
        }
        if (type == ValueType.STRING) {
            return unpacker.unpackString();
        }
        if (type == ValueType.BINARY) {
            return unpacker.readPayload(unpacker.unpackBinaryHeader());
        }
        if (type == ValueType.ARRAY) {
            final var size = unpacker.unpackArrayHeader();
            final var result = new ArrayList<Object>(size);
            for (int index = 0; index < size; index += 1) {
                result.add(unpackMsgPackValue(unpacker));
            }
            return result;
        }
        if (type == ValueType.MAP) {
            final var size = unpacker.unpackMapHeader();
            final var result = new LinkedHashMap<Object, Object>(size);
            for (int index = 0; index < size; index += 1) {
                final var key = unpackMsgPackValue(unpacker);
                final var value = unpackMsgPackValue(unpacker);
                result.put(key, value);
            }
            return result;
        }
        throw new IOException("unsupported msgpack value type: " + type);
    }

    private static Object narrowInteger(BigInteger value) {
        if (value.compareTo(BigInteger.valueOf(Integer.MIN_VALUE)) >= 0
                && value.compareTo(BigInteger.valueOf(Integer.MAX_VALUE)) <= 0) {
            return value.intValue();
        }
        if (value.compareTo(BigInteger.valueOf(Long.MIN_VALUE)) >= 0
                && value.compareTo(BigInteger.valueOf(Long.MAX_VALUE)) <= 0) {
            return value.longValue();
        }
        return value;
    }

    private static void packBinaryMsgPackValue(MessagePacker packer, Object value, BinaryEncoding binaryEncoding)
            throws IOException {
        if (value instanceof Map<?, ?> map) {
            packer.packMapHeader(map.size());
            for (final var entry : map.entrySet()) {
                final var key = entry.getKey();
                if (key instanceof String s && binaryEncoding.encodeMap.containsKey(s)) {
                    packer.packInt(binaryEncoding.encodeMap.get(s));
                } else {
                    packMsgPackValue(packer, key);
                }
                packBinaryMsgPackValue(packer, entry.getValue(), binaryEncoding);
            }
        } else if (value instanceof List<?> list) {
            if (packUniformMapArray(packer, list, binaryEncoding)) {
                return;
            }
            packer.packArrayHeader(list.size());
            for (final var item : list) {
                packBinaryMsgPackValue(packer, item, binaryEncoding);
            }
        } else {
            packMsgPackValue(packer, value);
        }
    }

    private static boolean packUniformMapArray(MessagePacker packer, List<?> list, BinaryEncoding binaryEncoding)
            throws IOException {
        if (binaryEncoding == null || list.size() < 16 || !(list.get(0) instanceof Map<?, ?> first) || first.isEmpty()) {
            return false;
        }

        final var rawKeys = new ArrayList<Object>(first.size());
        final var encodedKeys = new ArrayList<Integer>(first.size());
        for (final var entry : first.entrySet()) {
            if (!(entry.getKey() instanceof String key)) {
                return false;
            }
            final var encoded = binaryEncoding.encodeMap.get(key);
            if (encoded == null) {
                return false;
            }
            rawKeys.add(key);
            encodedKeys.add(encoded);
        }

        packer.packArrayHeader(list.size());
        for (final var item : list) {
            final var row = (Map<?, ?>) item;
            packer.packMapHeader(rawKeys.size());
            for (int index = 0; index < rawKeys.size(); index += 1) {
                packer.packInt(encodedKeys.get(index));
                packBinaryMsgPackValue(packer, row.get(rawKeys.get(index)), binaryEncoding);
            }
        }
        return true;
    }

    private static Object unpackBinaryMsgPackValue(MessageUnpacker unpacker, BinaryEncoding binaryEncoding)
            throws IOException {
        final var format = unpacker.getNextFormat();
        final ValueType type = format.getValueType();
        if (type == ValueType.ARRAY) {
            final var size = unpacker.unpackArrayHeader();
            final var result = new ArrayList<Object>(size);
            if (size >= 16 && unpacker.getNextFormat().getValueType() == ValueType.MAP) {
                final var first = unpackBinaryMsgPackMap(unpacker, binaryEncoding, null, null);
                result.add(first.value);
                for (int index = 1; index < size; index += 1) {
                    if (unpacker.getNextFormat().getValueType() == ValueType.MAP) {
                        result.add(unpackBinaryMsgPackMap(unpacker, binaryEncoding, first.rawKeys, first.decodedKeys).value);
                    } else {
                        result.add(unpackBinaryMsgPackValue(unpacker, binaryEncoding));
                    }
                }
                return result;
            }
            for (int index = 0; index < size; index += 1) {
                result.add(unpackBinaryMsgPackValue(unpacker, binaryEncoding));
            }
            return result;
        }
        if (type == ValueType.MAP) {
            return unpackBinaryMsgPackMap(unpacker, binaryEncoding, null, null).value;
        }
        return unpackMsgPackValue(unpacker);
    }

    private record DecodedMap(LinkedHashMap<String, Object> value, List<Object> rawKeys, List<String> decodedKeys) {
    }

    private static DecodedMap unpackBinaryMsgPackMap(
            MessageUnpacker unpacker,
            BinaryEncoding binaryEncoding,
            List<Object> expectedRawKeys,
            List<String> expectedDecodedKeys) throws IOException {
        final var size = unpacker.unpackMapHeader();
        final var result = new LinkedHashMap<String, Object>(size);
        final var collectKeys = expectedRawKeys == null || expectedDecodedKeys == null;
        final var rawKeys = collectKeys ? new ArrayList<Object>(size) : expectedRawKeys;
        final var decodedKeys = collectKeys ? new ArrayList<String>(size) : expectedDecodedKeys;
        final var canReuseKeys = !collectKeys && expectedRawKeys.size() == size;

        for (int index = 0; index < size; index += 1) {
            final var key = unpackMsgPackValue(unpacker);
            final var value = unpackBinaryMsgPackValue(unpacker, binaryEncoding);
            final String decodedKey;
            if (canReuseKeys && Objects.equals(key, expectedRawKeys.get(index))) {
                decodedKey = expectedDecodedKeys.get(index);
            } else {
                decodedKey = decodeBinaryKey(key, binaryEncoding);
            }
            if (collectKeys) {
                rawKeys.add(key);
                decodedKeys.add(decodedKey);
            }
            result.put(decodedKey, value);
        }
        return new DecodedMap(result, rawKeys, decodedKeys);
    }

    private static String decodeBinaryKey(Object key, BinaryEncoding binaryEncoding) {
        if (key instanceof String s) {
            return s;
        }
        if (key instanceof Number n) {
            final var index = n.intValue();
            try {
                final var decoded = binaryEncoding.decodeTable[index];
                if (decoded != null) {
                    return decoded;
                }
            } catch (RuntimeException ignored) {
            }
        }
        throw new BinaryEncodingMissing(key);
    }

    private static Map<String, Object> toStringMap(Object value) throws IOException {
        if (!(value instanceof Map<?, ?> raw)) {
            throw new IOException("expected msgpack map");
        }
        final var result = new LinkedHashMap<String, Object>(raw.size());
        for (final var entry : raw.entrySet()) {
            result.put(String.valueOf(entry.getKey()), entry.getValue());
        }
        return result;
    }

}
