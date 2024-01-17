package io.github.brenbar.uapi;

/**
 * A serialization implementation that converts between pseudo-JSON Objects and
 * byte array JSON payloads.
 * 
 * Pseudo-JSON objects are defined as data structures that represent JSON
 * objects as Maps and JSON arrays as Lists.
 */
public interface SerializationImpl {

    byte[] toJson(Object message);

    byte[] toMsgPack(Object message);

    Object fromJson(byte[] bytes);

    Object fromMsgPack(byte[] bytes);
}
