package uapi;

/**
 * A serialization implementation that converts between pseudo-JSON Objects and
 * byte array JSON payloads.
 * 
 * Pseudo-JSON objects are defined as data structures that represent JSON
 * objects as Maps and JSON arrays as Lists.
 */
public interface Serialization {

    byte[] toJson(Object message) throws Throwable;

    byte[] toMsgPack(Object message) throws Throwable;

    Object fromJson(byte[] bytes) throws Throwable;

    Object fromMsgPack(byte[] bytes) throws Throwable;
}
