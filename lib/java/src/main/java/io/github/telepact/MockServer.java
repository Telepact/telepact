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

import static io.github.telepact.internal.mock.MockHandle.mockHandle;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

import io.github.telepact.internal.mock.MockInvocation;
import io.github.telepact.internal.mock.MockStub;

/**
 * A Mock instance of a telepact server.
 */
public class MockServer {

    /**
     * Options for configuring the MockServer.
     */
    public static class Options {

        /**
         * Creates a new instance of Options with default values.
         */
        public Options() {
        }

        /**
         * Handler for errors thrown during message processing.
         */
        public Consumer<Throwable> onError = (e) -> {
        };

        /**
         * Flag to indicate if message responses should be randomly generated when no
         * stub is available.
         */
        public boolean enableMessageResponseGeneration = true;

        /**
         * Flag to indicate if optional fields should be included in generated
         * responses.
         */
        public boolean enableOptionalFieldGeneration = true;

        /**
         * Flag to indicate if optional fields, if enabled for generation, should be
         * randomly generated rather than always.
         */
        public boolean randomizeOptionalFieldGeneration = true;

        /**
         * Minimum length for randomly generated arrays and objects.
         */
        public int generatedCollectionLengthMin = 0;

        /**
         * Maximum length for randomly generated arrays and objects.
         */
        public int generatedCollectionLengthMax = 3;
    }

    private final Server server;
    private final RandomGenerator random;
    private final boolean enableGeneratedDefaultStub;
    private final boolean enableOptionalFieldGeneration;
    private final boolean randomizeOptionalFieldGeneration;

    private final List<MockStub> stubs = new ArrayList<>();
    private final List<MockInvocation> invocations = new ArrayList<>();

    /**
     * Create a mock server with the given telepact Schema.
     * 
     * @param mockTelepactSchema the mock telepact schema
     * @param options the options for the mock server
     */
    public MockServer(MockTelepactSchema mockTelepactSchema, Options options) {
        this.random = new RandomGenerator(options.generatedCollectionLengthMin, options.generatedCollectionLengthMax);
        this.enableGeneratedDefaultStub = options.enableMessageResponseGeneration;
        this.enableOptionalFieldGeneration = options.enableOptionalFieldGeneration;
        this.randomizeOptionalFieldGeneration = options.randomizeOptionalFieldGeneration;

        final var serverOptions = new Server.Options();
        serverOptions.onError = options.onError;
        serverOptions.authRequired = false;

        final var telepactSchema = new TelepactSchema(mockTelepactSchema.original, mockTelepactSchema.parsed,
                mockTelepactSchema.parsedRequestHeaders, mockTelepactSchema.parsedResponseHeaders);

        this.server = new Server(telepactSchema, this::handle, serverOptions);
    }

    /**
     * Process a given telepact Request Message into a telepact Response Message.
     * 
     * @param message the request message bytes
     * @return the response message bytes
     */
    public byte[] process(byte[] message) {
        return this.server.process(message);
    }

    private Message handle(Message requestMessage) {
        return mockHandle(requestMessage, this.stubs, this.invocations, this.random,
                this.server.telepactSchema, this.enableGeneratedDefaultStub, this.enableOptionalFieldGeneration,
                this.randomizeOptionalFieldGeneration);
    }
}
