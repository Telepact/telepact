package io.github.msgpact;

import static io.github.msgpact.internal.mock.MockHandle.mockHandle;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

import io.github.msgpact.internal.mock.MockInvocation;
import io.github.msgpact.internal.mock.MockStub;

/**
 * A Mock instance of a msgPact server.
 */
public class MockServer {

    /**
     * Options for the MockServer.
     */
    public static class Options {

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
     * Create a mock server with the given msgPact Schema.
     * 
     * @param msgPactSchemaAsJson
     */
    public MockServer(MockMsgPactSchema mockMsgPactSchema, Options options) {
        this.random = new RandomGenerator(options.generatedCollectionLengthMin, options.generatedCollectionLengthMax);
        this.enableGeneratedDefaultStub = options.enableMessageResponseGeneration;
        this.enableOptionalFieldGeneration = options.enableOptionalFieldGeneration;
        this.randomizeOptionalFieldGeneration = options.randomizeOptionalFieldGeneration;

        final var serverOptions = new Server.Options();
        serverOptions.onError = options.onError;
        serverOptions.authRequired = false;

        final var msgPactSchema = new MsgPactSchema(mockMsgPactSchema.original, mockMsgPactSchema.parsed,
                mockMsgPactSchema.parsedRequestHeaders, mockMsgPactSchema.parsedResponseHeaders);

        this.server = new Server(msgPactSchema, this::handle, serverOptions);
    }

    /**
     * Process a given msgPact Request Message into a msgPact Response Message.
     * 
     * @param requestMessageBytes
     * @return
     */
    public byte[] process(byte[] message) {
        return this.server.process(message);
    }

    private Message handle(Message requestMessage) {
        return mockHandle(requestMessage, this.stubs, this.invocations, this.random,
                this.server.msgPactSchema, this.enableGeneratedDefaultStub, this.enableOptionalFieldGeneration,
                this.randomizeOptionalFieldGeneration);
    }
}
