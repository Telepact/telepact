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

import java.util.Map;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.telepact.internal.binary.BinaryEncoding;
import io.github.telepact.internal.binary.BinaryMsgPackCodec;
import io.github.telepact.internal.binary.BinaryMsgPackSerialization;

class DefaultSerialization implements Serialization, BinaryMsgPackSerialization {

    private final ObjectMapper jsonMapper = new ObjectMapper();
    private final BinaryMsgPackCodec binaryMsgPack = new BinaryMsgPackCodec();

    @Override
    public byte[] toJson(Object telepactMessage) throws Throwable {
        return jsonMapper.writeValueAsBytes(telepactMessage);
    }

    @Override
    public byte[] toMsgPack(Object telepactMessage) throws Throwable {
        return binaryMsgPack.toMsgPack(telepactMessage);
    }

    @Override
    public Object fromJson(byte[] bytes) throws Throwable {
        return jsonMapper.readValue(bytes, new TypeReference<Object>() {
        });
    }

    @Override
    public Object fromMsgPack(byte[] bytes) throws Throwable {
        return binaryMsgPack.fromMsgPack(bytes);
    }

    @Override
    public byte[] toBinaryMsgPack(Map<String, Object> headers, Map<String, Object> body,
            BinaryEncoding binaryEncoding) throws Throwable {
        return binaryMsgPack.toBinaryMsgPack(headers, body, binaryEncoding);
    }

    @Override
    public MsgPackHeaders fromMsgPackHeaders(byte[] bytes) throws Throwable {
        return binaryMsgPack.fromMsgPackHeaders(bytes);
    }

    @Override
    public Map<String, Object> fromMsgPackBody(byte[] bytes, int offset, BinaryEncoding binaryEncoding)
            throws Throwable {
        return binaryMsgPack.fromMsgPackBody(bytes, offset, binaryEncoding);
    }
}
