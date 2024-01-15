package io.github.brenbar.uapi;

/**
 * A serialization implementation.
 */
public interface SerializationImpl {

    byte[] toJson(Object uapiMessage);

    byte[] toMsgPack(Object uapiMessage);

    Object fromJson(byte[] bytes);

    Object fromMsgPack(byte[] bytes);
}
