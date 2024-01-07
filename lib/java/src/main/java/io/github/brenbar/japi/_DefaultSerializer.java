package io.github.brenbar.japi;

import java.io.IOException;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;

import org.msgpack.jackson.dataformat.MessagePackFactory;
import org.msgpack.jackson.dataformat.MessagePackParser;

import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonDeserializer;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.KeyDeserializer;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.deser.NullValueProvider;
import com.fasterxml.jackson.databind.deser.impl.JDKValueInstantiators;
import com.fasterxml.jackson.databind.deser.std.MapDeserializer;
import com.fasterxml.jackson.databind.deser.std.UntypedObjectDeserializer;
import com.fasterxml.jackson.databind.jsontype.TypeDeserializer;
import com.fasterxml.jackson.databind.module.SimpleModule;
import com.fasterxml.jackson.databind.type.TypeFactory;

class _DefaultSerializer implements SerializationImpl {

    static class MessagePackMapDeserializer extends MapDeserializer {

        public static KeyDeserializer keyDeserializer = new KeyDeserializer() {

            @Override
            public Object deserializeKey(String s, DeserializationContext deserializationContext) throws IOException {
                JsonParser parser = deserializationContext.getParser();
                if (parser instanceof MessagePackParser p) {
                    if (p.isCurrentFieldId()) {
                        return Long.valueOf(s);
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
    public byte[] toJson(Object japiMessage) {
        try {
            return jsonMapper.writeValueAsBytes(japiMessage);
        } catch (JsonProcessingException e) {
            throw new SerializationError(e);
        }
    }

    public byte[] toMsgPack(Object japiMessage) {
        try {
            return binaryMapper.writeValueAsBytes(japiMessage);
        } catch (JsonProcessingException e) {
            throw new SerializationError(e);
        }
    }

    @Override
    public Object fromJson(byte[] bytes) {
        try {
            return jsonMapper.readValue(bytes, new TypeReference<Object>() {
            });
        } catch (JsonParseException e) {
            throw new DeserializationError(new InvalidJsonError(e));
        } catch (IOException e) {
            throw new DeserializationError(e);
        }
    }

    @Override
    public Object fromMsgPack(byte[] bytes) {
        try {
            return binaryMapper.readValue(bytes, new TypeReference<Object>() {
            });
        } catch (IOException e) {
            throw new DeserializationError(e);
        }
    }

}