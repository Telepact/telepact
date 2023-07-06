package io.github.brenbar.japi;

import com.fasterxml.jackson.databind.deser.std.UntypedObjectDeserializer;
import com.fasterxml.jackson.databind.type.TypeFactory;

import java.util.Map;

class MessagePackUntypedObjectDeserializer extends UntypedObjectDeserializer {

    public MessagePackUntypedObjectDeserializer() {
        super(null, TypeFactory.defaultInstance().constructMapType(Map.class, Object.class, Object.class));
    }
}