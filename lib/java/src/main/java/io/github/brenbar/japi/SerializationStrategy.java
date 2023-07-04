package io.github.brenbar.japi;

import java.util.List;

public interface SerializationStrategy {

    byte[] toJson(List<Object> japiMessage);

    byte[] toMsgPack(List<Object> japiMessage);

    List<Object> fromJson(byte[] bytes) throws DeserializationError;

    List<Object> fromMsgPack(byte[] bytes) throws DeserializationError;
}
