package io.github.brenbar.japi;

/**
 * A serialization implementation.
 */
public interface SerializationImpl {

    byte[] toJson(Object japiMessage);

    byte[] toMsgPack(Object japiMessage);

    Object fromJson(byte[] bytes);

    Object fromMsgPack(byte[] bytes);
}
