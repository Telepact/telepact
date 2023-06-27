package io.github.brenbar.japi;

import java.util.List;

public interface Serializer {

    byte[] serializeToJson(List<Object> japiMessage);

    byte[] serializeToMsgPack(List<Object> japiMessage);

    List<Object> deserializeFromJson(byte[] bytes) throws DeserializationError;

    List<Object> deserializeFromMsgPack(byte[] bytes) throws DeserializationError;
}
