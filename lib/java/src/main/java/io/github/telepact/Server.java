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

import static io.github.telepact.internal.ProcessBytes.processBytes;
import static io.github.telepact.internal.binary.ConstructBinaryEncoding.constructBinaryEncoding;

import java.util.function.Consumer;
import java.util.function.Function;

import io.github.telepact.internal.binary.ServerBinaryEncoder;
import io.github.telepact.internal.types.VStruct;

/**
 * A telepact Server.
 */
public class Server {

    /**
     * Options for the Server.
     */
    public static class Options {

        /**
         * Handler for errors thrown during message processing.
         */
        public Consumer<Throwable> onError = (e) -> {
        };

        /**
         * Execution hook that runs when a request Message is received.
         */
        public Consumer<Message> onRequest = (m) -> {
        };

        /**
         * Execution hook that runs when a response Message is about to be returned.
         */
        public Consumer<Message> onResponse = (m) -> {
        };

        /**
         * Flag to indicate if authentication via the _auth header is required.
         */
        public boolean authRequired = true;

        /**
         * The serialization implementation that should be used to serialize and
         * deserialize messages.
         */
        public Serialization serialization = new DefaultSerialization();
    }

    final TelepactSchema telepactSchema;
    private final Function<Message, Message> handler;
    private final Consumer<Throwable> onError;
    private final Consumer<Message> onRequest;
    private final Consumer<Message> onResponse;
    private final Serializer serializer;

    /**
     * Create a server with the given telepact schema and handler.
     * 
     * @param telepactSchemaAsJson
     * @param handler
     */
    public Server(TelepactSchema telepactSchema, Function<Message, Message> handler, Options options) {
        this.handler = handler;
        this.onError = options.onError;
        this.onRequest = options.onRequest;
        this.onResponse = options.onResponse;
        this.telepactSchema = telepactSchema;

        final var binaryEncoding = constructBinaryEncoding(this.telepactSchema);
        final var binaryEncoder = new ServerBinaryEncoder(binaryEncoding);
        this.serializer = new Serializer(options.serialization, binaryEncoder);

        if (!this.telepactSchema.parsed.containsKey("struct.Auth_") && options.authRequired) {
            throw new RuntimeException(
                    "Unauthenticated server. Either define a `struct.Auth_` in your schema or set `options.authRequired` to `false`.");
        }
    }

    /**
     * Process a given telepact Request Message into a telepact Response Message.
     * 
     * @param requestMessageBytes
     * @return
     */
    public byte[] process(byte[] requestMessageBytes) {
        return processBytes(requestMessageBytes, this.serializer, this.telepactSchema, this.onError,
                this.onRequest, this.onResponse, this.handler);
    }
}
