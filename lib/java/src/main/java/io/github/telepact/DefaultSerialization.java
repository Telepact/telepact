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
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.msgpack.jackson.dataformat.MessagePackFactory;
import org.msgpack.jackson.dataformat.MessagePackGenerator;
import org.msgpack.jackson.dataformat.MessagePackParser;

import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.ObjectCodec;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonDeserializer;
import com.fasterxml.jackson.databind.JsonSerializer;
import com.fasterxml.jackson.databind.KeyDeserializer;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializerProvider;
import com.fasterxml.jackson.databind.deser.NullValueProvider;
import com.fasterxml.jackson.databind.deser.impl.JDKValueInstantiators;
import com.fasterxml.jackson.databind.deser.std.MapDeserializer;
import com.fasterxml.jackson.databind.deser.std.UntypedObjectDeserializer;
import com.fasterxml.jackson.databind.jsontype.TypeDeserializer;
import com.fasterxml.jackson.databind.module.SimpleModule;
import com.fasterxml.jackson.databind.type.TypeFactory;

import io.github.telepact.internal.binary.BinaryEncodedBody;
import io.github.telepact.internal.binary.BinaryEncoding;

class DefaultSerialization implements Serialization {

    static class MessagePackMapDeserializer extends MapDeserializer {

        public static KeyDeserializer keyDeserializer = new KeyDeserializer() {

            @Override
            public Object deserializeKey(String s, DeserializationContext deserializationContext) throws IOException {
                JsonParser parser = deserializationContext.getParser();
                if (parser instanceof MessagePackParser) {
                    MessagePackParser p = (MessagePackParser) parser;
                    if (p.isCurrentFieldId()) {
                        return Integer.valueOf(s);
                    }
                }
                return s;
            }
        };

        public MessagePackMapDeserializer() {
            super(
                    TypeFactory.defaultInstance().constructMapType(Map.class, Object.class, Object.class),
                    JDKValueInstantiators.findStdValueInstantiator(null, LinkedHashMap.class),
                    keyDeserializer, null, null);
        }

        public MessagePackMapDeserializer(MapDeserializer src, KeyDeserializer keyDeser,
                JsonDeserializer<Object> valueDeser, TypeDeserializer valueTypeDeser, NullValueProvider nuller,
                Set<String> ignorable, Set<String> includable) {
            super(src, keyDeser, valueDeser, valueTypeDeser, nuller, ignorable, includable);
        }

        @Override
        protected MapDeserializer withResolved(KeyDeserializer keyDeser, TypeDeserializer valueTypeDeser,
                JsonDeserializer<?> valueDeser, NullValueProvider nuller, Set<String> ignorable,
                Set<String> includable) {
            return new MessagePackMapDeserializer(this, keyDeser, (JsonDeserializer<Object>) valueDeser, valueTypeDeser,
                    nuller, ignorable, includable);
        }
    }

    static class MessagePackUntypedObjectDeserializer extends UntypedObjectDeserializer {

        public MessagePackUntypedObjectDeserializer() {
            super(null, TypeFactory.defaultInstance().constructMapType(Map.class, Object.class, Object.class));
        }
    }

    static class BinaryEncodedBodySerializer extends JsonSerializer<BinaryEncodedBody> {
        @Override
        public void serialize(BinaryEncodedBody value, JsonGenerator gen, SerializerProvider serializers) throws IOException {
            writeBinaryValue(gen, value.value, value.binaryEncoding);
        }

        private void writeBinaryValue(JsonGenerator gen, Object value, BinaryEncoding binaryEncoding) throws IOException {
            if (value == null) {
                gen.writeNull();
                return;
            }
            if (value instanceof BinaryEncodedBody wrapped) {
                writeBinaryValue(gen, wrapped.value, wrapped.binaryEncoding);
                return;
            }
            if (value instanceof Map<?, ?> map) {
                gen.writeStartObject();
                for (final var entry : map.entrySet()) {
                    writeBinaryFieldName(gen, entry.getKey(), binaryEncoding);
                    writeBinaryValue(gen, entry.getValue(), binaryEncoding);
                }
                gen.writeEndObject();
                return;
            }
            if (value instanceof List<?> list) {
                gen.writeStartArray();
                for (final var item : list) {
                    writeBinaryValue(gen, item, binaryEncoding);
                }
                gen.writeEndArray();
                return;
            }
            gen.writeObject(value);
        }

        private void writeBinaryFieldName(JsonGenerator gen, Object key, BinaryEncoding binaryEncoding) throws IOException {
            if (key instanceof final String stringKey) {
                final Integer mapped = binaryEncoding == null ? null : binaryEncoding.encodeMap.get(stringKey);
                if (mapped != null) {
                    writeIntegerFieldName(gen, mapped.longValue());
                    return;
                }
                gen.writeFieldName(stringKey);
                return;
            }
            if (key instanceof final Number numberKey) {
                writeIntegerFieldName(gen, numberKey.longValue());
                return;
            }
            gen.writeFieldName(String.valueOf(key));
        }

        private void writeIntegerFieldName(JsonGenerator gen, long value) throws IOException {
            if (gen instanceof MessagePackGenerator messagePackGenerator) {
                messagePackGenerator.writeFieldId(value);
                return;
            }
            gen.writeFieldName(Long.toString(value));
        }
    }

    private ObjectMapper jsonMapper = new ObjectMapper();
    private ObjectMapper binaryMapper = new ObjectMapper(new MessagePackFactory()
            .setSupportIntegerKeys(true))
            .registerModule(new SimpleModule()
                    .addDeserializer(Object.class,
                            (JsonDeserializer<Object>) new MessagePackUntypedObjectDeserializer())
                    .addDeserializer(Map.class, new MessagePackMapDeserializer())
                    .addSerializer(BinaryEncodedBody.class, new BinaryEncodedBodySerializer()));

    @Override
    public byte[] toJson(Object telepactMessage) throws Throwable {
        return jsonMapper.writeValueAsBytes(telepactMessage);
    }

    public byte[] toMsgPack(Object telepactMessage) throws Throwable {
        return binaryMapper.writeValueAsBytes(telepactMessage);
    }

    @Override
    public Object fromJson(byte[] bytes) throws Throwable {
        return jsonMapper.readValue(bytes, new TypeReference<Object>() {
        });
    }

    @Override
    public Object fromMsgPack(byte[] bytes) throws Throwable {
        return binaryMapper.readValue(bytes, new TypeReference<Object>() {
        });
    }
}
