package io.github.brenbar.japi;

import java.io.IOException;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;

import org.msgpack.jackson.dataformat.MessagePackParser;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonDeserializer;
import com.fasterxml.jackson.databind.KeyDeserializer;
import com.fasterxml.jackson.databind.deser.NullValueProvider;
import com.fasterxml.jackson.databind.deser.impl.JDKValueInstantiators;
import com.fasterxml.jackson.databind.deser.std.MapDeserializer;
import com.fasterxml.jackson.databind.jsontype.TypeDeserializer;
import com.fasterxml.jackson.databind.type.TypeFactory;

class MessagePackMapDeserializer extends MapDeserializer {

    public static KeyDeserializer keyDeserializer = new KeyDeserializer() {

        @Override
        public Object deserializeKey(String s, DeserializationContext deserializationContext) throws IOException {
            JsonParser parser = deserializationContext.getParser();
            if (parser instanceof MessagePackParser) {
                if (((MessagePackParser) parser).isCurrentFieldId()) {
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
            JsonDeserializer<?> valueDeser, NullValueProvider nuller, Set<String> ignorable, Set<String> includable) {
        return new MessagePackMapDeserializer(this, keyDeser, (JsonDeserializer<Object>) valueDeser, valueTypeDeser,
                nuller, ignorable, includable);
    }
}