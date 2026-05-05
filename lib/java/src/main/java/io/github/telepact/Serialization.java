//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
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
