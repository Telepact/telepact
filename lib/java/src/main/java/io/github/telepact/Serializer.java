//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact;

import static io.github.telepact.internal.DeserializeInternal.deserializeInternal;
import static io.github.telepact.internal.SerializeInternal.serializeInternal;

import io.github.telepact.internal.binary.Base64Encoder;
import io.github.telepact.internal.binary.BinaryEncoder;

/**
 * A serializer that converts a Message to and from a serialized form.
 */
public class Serializer {

    private Serialization serializationImpl;
    private BinaryEncoder binaryEncoder;
    private Base64Encoder base64Encoder;

    Serializer(Serialization serializationImpl, BinaryEncoder binaryEncoder, Base64Encoder base64Encoder) {
        this.serializationImpl = serializationImpl;
        this.binaryEncoder = binaryEncoder;
        this.base64Encoder = base64Encoder;
    }

    /**
     * Serialize a Message into a byte array.
     * 
     * @param message the object to be serialized
     * @return the serialized byte array
     */
    public byte[] serialize(Message message) {
        return serializeInternal(message, this.binaryEncoder, this.base64Encoder, this.serializationImpl);
    }

    /**
     * Deserialize a Message from a byte array.
     * 
     * @param messageBytes the byte array to be deserialized
     * @return the deserialized object
     */
    public Message deserialize(byte[] messageBytes) {
        return deserializeInternal(messageBytes, this.serializationImpl, this.binaryEncoder, this.base64Encoder);
    }
}