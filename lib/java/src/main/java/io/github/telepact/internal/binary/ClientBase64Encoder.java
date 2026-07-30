//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.binary;

import static io.github.telepact.internal.binary.ClientBase64Decode.clientBase64Decode;
import static io.github.telepact.internal.binary.ClientBase64Encode.clientBase64Encode;


import java.util.List;

public class ClientBase64Encoder implements Base64Encoder {

    @Override
    public List<Object> encode(List<Object> message) throws BinaryEncoderUnavailableError {
        clientBase64Encode(message);
        return message;
    }

    @Override
    public List<Object> decode(List<Object> message) throws BinaryEncoderUnavailableError {
        clientBase64Decode(message);
        return message;
    }
}