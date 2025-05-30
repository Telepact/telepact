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

package io.github.telepact.internal;

import java.util.List;
import java.util.Map;

import io.github.telepact.Message;
import io.github.telepact.Serialization;
import io.github.telepact.internal.binary.Base64Encoder;
import io.github.telepact.internal.binary.BinaryEncoder;
import io.github.telepact.internal.validation.InvalidMessage;
import io.github.telepact.internal.validation.InvalidMessageBody;

public class DeserializeInternal {

    public static Message deserializeInternal(byte[] messageBytes, Serialization serialization,
            BinaryEncoder binaryEncoder, Base64Encoder base64Encoder) {
        final Object messageAsPseudoJson;
        final boolean isMsgPack;

        try {
            if (messageBytes[0] == (byte) 0x92) { // MsgPack
                isMsgPack = true;
                messageAsPseudoJson = serialization.fromMsgPack(messageBytes);
            } else {
                isMsgPack = false;
                messageAsPseudoJson = serialization.fromJson(messageBytes);
            }
        } catch (Throwable e) {
            throw new InvalidMessage(e);
        }

        if (!(messageAsPseudoJson instanceof List)) {
            throw new InvalidMessage();
        }
        final List<Object> messageAsPseudoJsonList = (List<Object>) messageAsPseudoJson;

        if (messageAsPseudoJsonList.size() != 2) {
            throw new InvalidMessage();
        }

        final List<Object> finalMessageAsPseudoJsonList;
        if (isMsgPack) {
            finalMessageAsPseudoJsonList = binaryEncoder.decode(messageAsPseudoJsonList);
        } else {
            finalMessageAsPseudoJsonList = base64Encoder.decode(messageAsPseudoJsonList);
        }

        if (!(finalMessageAsPseudoJsonList.get(0) instanceof Map)) {
            throw new InvalidMessage();
        }
        Map<String, Object> headers = (Map<String, Object>) finalMessageAsPseudoJsonList.get(0);

        if (!(finalMessageAsPseudoJsonList.get(1) instanceof Map)) {
            throw new InvalidMessage();
        }
        Map<String, Object> body = (Map<String, Object>) finalMessageAsPseudoJsonList.get(1);

        if (body.size() != 1) {
            throw new InvalidMessageBody();
        }

        if (!(body.values().stream().findAny().get() instanceof Map)) {
            throw new InvalidMessageBody();
        }

        return new Message(headers, body);
    }
}
