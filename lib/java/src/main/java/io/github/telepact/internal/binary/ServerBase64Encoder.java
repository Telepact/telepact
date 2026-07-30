//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.binary;

import static io.github.telepact.internal.binary.ServerBase64Encode.serverBase64Encode;

import java.util.List;

public class ServerBase64Encoder implements Base64Encoder {

    @Override
    public List<Object> encode(List<Object> message) throws BinaryEncoderUnavailableError {
        // Server manually runs decode logic after its validation
        return message;
    }

    @Override
    public List<Object> decode(List<Object> message) throws BinaryEncoderUnavailableError {
        serverBase64Encode(message);
        return message;
    }
}