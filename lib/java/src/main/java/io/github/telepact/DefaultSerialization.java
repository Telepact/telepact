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
import java.io.OutputStream;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;

import org.msgpack.core.MessagePack;
import org.msgpack.core.MessagePack.PackerConfig;
import org.msgpack.jackson.dataformat.MessagePackFactory;
import org.msgpack.jackson.dataformat.MessagePackGenerator;
import org.msgpack.jackson.dataformat.MessagePackParser;

import com.fasterxml.jackson.core.JsonEncoding;
import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.ObjectCodec;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonDeserializer;
import com.fasterxml.jackson.databind.KeyDeserializer;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.deser.NullValueProvider;
import com.fasterxml.jackson.databind.deser.impl.JDKValueInstantiators;
import com.fasterxml.jackson.databind.deser.std.MapDeserializer;
import com.fasterxml.jackson.databind.deser.std.UntypedObjectDeserializer;
import com.fasterxml.jackson.databind.jsontype.TypeDeserializer;
import com.fasterxml.jackson.databind.module.SimpleModule;
import com.fasterxml.jackson.databind.type.TypeFactory;

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

    private ObjectMapper jsonMapper = new ObjectMapper();
    private ObjectMapper binaryMapper = new ObjectMapper(new MessagePackFactory())
            .registerModule(new SimpleModule()
                    .addDeserializer(Object.class,
                            (JsonDeserializer<Object>) new MessagePackUntypedObjectDeserializer())
                    .addDeserializer(Map.class, new MessagePackMapDeserializer()));

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