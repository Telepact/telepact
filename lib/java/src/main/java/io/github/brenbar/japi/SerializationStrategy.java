package io.github.brenbar.japi;

import java.util.List;

/**
 * A serialization implementation.
 */
public interface SerializationStrategy {

    byte[] toJson(List<Object> japiMessage);

    byte[] toMsgPack(List<Object> japiMessage);

    List<Object> fromJson(byte[] bytes);

    List<Object> fromMsgPack(byte[] bytes);
}
