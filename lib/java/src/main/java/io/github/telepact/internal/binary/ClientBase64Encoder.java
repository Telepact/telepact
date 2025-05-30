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