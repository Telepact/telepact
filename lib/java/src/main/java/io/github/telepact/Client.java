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

import static io.github.telepact.internal.ProcessRequestObject.processRequestObject;

import java.util.concurrent.Future;
import java.util.function.BiFunction;

import io.github.telepact.internal.binary.ClientBinaryEncoder;

/**
 * A telepact client.
 */
public class Client {

    /**
     * Options for the Client.
     */
    public static class Options {

        /**
         * Indicates if the client should use binary payloads instead of JSON.
         */
        public boolean useBinary = false;

        /**
         * Indicates if the client should always send JSON payloads, even if binary
         * is enabled.
         */
        public boolean alwaysSendJson = true;

        /**
         * Indicates the default timeout that should be used if the _tim header is not
         * set.
         */
        public long timeoutMsDefault = 5000;

        /**
         * The serialization implementation that should be used to serialize and
         * deserialize messages.
         */
        public Serialization serializationImpl = new DefaultSerialization();

        /**
         * The client binary strategy that should be used to maintain binary
         * compatibility with the server.
         */
        public ClientBinaryStrategy binaryStrategy = new DefaultClientBinaryStrategy();
    }

    private final BiFunction<Message, Serializer, Future<Message>> adapter;
    private final Serializer serializer;
    private final boolean useBinaryDefault;
    private final boolean alwaysSendJson;
    private final long timeoutMsDefault;

    /**
     * Create a client with the given transport adapter.
     * 
     * Example transport adapter:
     * 
     * <pre>
     * var adapter = (requestMessage, serializer) -> {
     *     return CompletableFuture.supplyAsync(() -> {
     *         var requestMessageBytes = serializer.serialize(requestMessage);
     *         var responseMessageBytes = YOUR_TRANSPORT.transport(requestMessageBytes);
     *         responseMessage = serializer.deserialize(responseMessageBytes);
     *         return responseMessage;
     *     });
     * };
     * </pre>
     * 
     * @param adapter
     */
    public Client(BiFunction<Message, Serializer, Future<Message>> adapter, Options options) {
        this.adapter = adapter;
        this.useBinaryDefault = options.useBinary;
        this.alwaysSendJson = options.alwaysSendJson;
        this.timeoutMsDefault = options.timeoutMsDefault;
        this.serializer = new Serializer(options.serializationImpl,
                new ClientBinaryEncoder(options.binaryStrategy));
    }

    /**
     * Submit a telepact Request Message. Returns a telepact Response Message.
     * 
     * @param request
     * @return
     */
    public Message request(Message requestMessage) {
        return processRequestObject(requestMessage, this.adapter, this.serializer,
                this.timeoutMsDefault, this.useBinaryDefault, this.alwaysSendJson);
    }

}
