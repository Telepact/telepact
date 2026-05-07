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

import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Future;
import java.util.function.Consumer;

import io.github.telepact.internal.CreateInternalFunctionRoutes;
import io.github.telepact.internal.binary.ServerBase64Encoder;
import io.github.telepact.internal.binary.ServerBinaryEncoder;

/**
 * A telepact Server.
 */
public class Server {

    @FunctionalInterface
    public interface Middleware {
        Message apply(Message requestMessage, FunctionRouter functionRouter);
    }

    @FunctionalInterface
    public interface AuthHandler {
        Future<Map<String, Object>> apply(Map<String, Object> headers);
    }

    /**
     * Options for configuring the Server.
     */
    public static class Options {

        /**
         * Default constructor for Options.
         * Initializes the configuration options with default values.
         */
        public Options() {
        }

        /**
         * Handler for errors thrown during message processing.
         */
        public Consumer<TelepactError> onError = (e) -> {
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
         * Execution hook that runs when auth headers are present and can add derived
         * request headers.
         */
        public AuthHandler onAuth = (headers) -> CompletableFuture.completedFuture(Map.of());

        /**
         * Middleware that can wrap function routing.
         */
        public Middleware middleware = (requestMessage, functionRouter) -> functionRouter.route(requestMessage);

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
    private final FunctionRouter functionRouter;
    private final Middleware middleware;
    private final Consumer<TelepactError> onError;
    private final Consumer<Message> onRequest;
    private final Consumer<Message> onResponse;
    private final AuthHandler onAuth;
    private final Serializer serializer;

    /**
     * Create a server with the given telepact schema and function router.
     * 
     * @param telepactSchema The schema to be used by the server.
     * @param functionRouter The function router to handle incoming messages.
     * @param options The options for configuring the server.
     */
    public Server(TelepactSchema telepactSchema, FunctionRouter functionRouter, Options options) {
        functionRouter.functionRoutes().putAll(CreateInternalFunctionRoutes.createInternalFunctionRoutes(telepactSchema));
        this.functionRouter = functionRouter;
        this.middleware = options.middleware;
        this.onError = options.onError;
        this.onRequest = options.onRequest;
        this.onResponse = options.onResponse;
        this.onAuth = options.onAuth;
        this.telepactSchema = telepactSchema;

        final var binaryEncoding = constructBinaryEncoding(this.telepactSchema);
        final var binaryEncoder = new ServerBinaryEncoder(binaryEncoding);
        final var base64Encoder = new ServerBase64Encoder();

        this.serializer = new Serializer(options.serialization, binaryEncoder, base64Encoder);

        if (!this.telepactSchema.parsed.containsKey("union.Auth_") && options.authRequired) {
            throw new RuntimeException(
                    "Unauthenticated server. Either define a `union.Auth_` in your schema or set `options.authRequired` to `false`.");
        }
    }

    /**
     * Process a given telepact Request Message into a telepact Response Message.
     * 
     * @param requestMessageBytes The bytes of the request message to be processed.
     * @return The bytes of the response message.
     */
    public Response process(byte[] requestMessageBytes) {
        return processBytes(requestMessageBytes, null, this.serializer, this.telepactSchema, this.onError,
                this.onRequest, this.onResponse, this.onAuth, this.middleware, this.functionRouter);
    }

    /**
     * Process a given telepact Request Message into a telepact Response Message.
     * 
     * @param requestMessageBytes The bytes of the request message to be processed.
     * @param updateHeaders Callback that can update the mutable request headers
     *            before request handling continues.
     * @return The bytes of the response message.
     */
    public Response process(byte[] requestMessageBytes, Consumer<Map<String, Object>> updateHeaders) {
        return processBytes(requestMessageBytes, updateHeaders, this.serializer, this.telepactSchema, this.onError,
                this.onRequest, this.onResponse, this.onAuth, this.middleware, this.functionRouter);
    }
}
