//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact;

/**
 * A serialization implementation that converts between pseudo-JSON Objects and
 * byte array JSON payloads.
 * 
 * Pseudo-JSON objects are defined as data structures that represent JSON
 * objects as Maps and JSON arrays as Lists.
 */
public interface Serialization {

    /**
     * Serializes an object to JSON format.
     *
     * @param message the object to serialize
     * @return the serialized JSON as a byte array
     * @throws Throwable if serialization fails
     */
    byte[] toJson(Object message) throws Throwable;

    /**
     * Serializes an object to MessagePack format.
     *
     * @param message the object to serialize
     * @return the serialized MessagePack as a byte array
     * @throws Throwable if serialization fails
     */
    byte[] toMsgPack(Object message) throws Throwable;

    /**
     * Deserializes a JSON byte array to an object.
     *
     * @param bytes the JSON byte array
     * @return the deserialized object
     * @throws Throwable if deserialization fails
     */
    Object fromJson(byte[] bytes) throws Throwable;

    /**
     * Deserializes a MessagePack byte array to an object.
     *
     * @param bytes the MessagePack byte array
     * @return the deserialized object
     * @throws Throwable if deserialization fails
     */
    Object fromMsgPack(byte[] bytes) throws Throwable;
}
