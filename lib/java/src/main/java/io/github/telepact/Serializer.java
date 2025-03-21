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

import static io.github.telepact.internal.DeserializeInternal.deserializeInternal;
import static io.github.telepact.internal.SerializeInternal.serializeInternal;

import io.github.telepact.internal.binary.BinaryEncoder;

/**
 * A serializer that converts a Message to and from a serialized form.
 */
public class Serializer {

    private Serialization serializationImpl;
    private BinaryEncoder binaryEncoder;

    Serializer(Serialization serializationImpl, BinaryEncoder binaryEncoder) {
        this.serializationImpl = serializationImpl;
        this.binaryEncoder = binaryEncoder;
    }

    /**
     * Serialize a Message into a byte array.
     * 
     * @param message
     * @return
     */
    public byte[] serialize(Message message) {
        return serializeInternal(message, this.binaryEncoder, this.serializationImpl);
    }

    /**
     * Deserialize a Message from a byte array.
     * 
     * @param messageBytes
     * @return
     */
    public Message deserialize(byte[] messageBytes) {
        return deserializeInternal(messageBytes, this.serializationImpl, this.binaryEncoder);
    }
}