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

import static io.github.telepact.internal.binary.ConstructBinaryEncoding.constructBinaryEncoding;

import io.github.telepact.internal.binary.ClientBase64Encoder;
import io.github.telepact.internal.binary.ClientBinaryEncoder;
import io.github.telepact.internal.binary.DefaultBinaryEncodingCache;
import io.github.telepact.internal.binary.ServerBase64Encoder;
import io.github.telepact.internal.binary.ServerBinaryEncoder;

public final class SerializerFactory {
    private SerializerFactory() {
    }

    public static Serializer createClientSerializer() {
        return createClientSerializer(new DefaultSerialization());
    }

    public static Serializer createClientSerializer(Serialization serialization) {
        return new Serializer(
                serialization,
                new ClientBinaryEncoder(new DefaultBinaryEncodingCache()),
                new ClientBase64Encoder());
    }

    public static Serializer createServerSerializer(TelepactSchema telepactSchema) {
        return createServerSerializer(telepactSchema, new DefaultSerialization());
    }

    public static Serializer createServerSerializer(TelepactSchema telepactSchema, Serialization serialization) {
        return new Serializer(
                serialization,
                new ServerBinaryEncoder(constructBinaryEncoding(telepactSchema)),
                new ServerBase64Encoder());
    }
}
