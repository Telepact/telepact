package uapi;

import static uapi.internal.mock.MockHandle.mockHandle;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

import uapi.internal.mock.MockInvocation;
import uapi.internal.mock.MockStub;

/**
 * A Mock instance of a uAPI server.
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
     * Create a mock server with the given uAPI Schema.
     * 
     * @param uApiSchemaAsJson
     */
    public MockServer(MockUApiSchema mockUApiSchema, Options options) {
        this.random = new RandomGenerator(options.generatedCollectionLengthMin, options.generatedCollectionLengthMax);
        this.enableGeneratedDefaultStub = options.enableMessageResponseGeneration;
        this.enableOptionalFieldGeneration = options.enableOptionalFieldGeneration;
        this.randomizeOptionalFieldGeneration = options.randomizeOptionalFieldGeneration;

        final var serverOptions = new Server.Options();
        serverOptions.onError = options.onError;
        serverOptions.authRequired = false;

        final var uApiSchema = new UApiSchema(mockUApiSchema.original, mockUApiSchema.parsed,
                mockUApiSchema.parsedRequestHeaders, mockUApiSchema.parsedResponseHeaders);

        this.server = new Server(uApiSchema, this::handle, serverOptions);
    }

    /**
     * Process a given uAPI Request Message into a uAPI Response Message.
     * 
     * @param requestMessageBytes
     * @return
     */
    public byte[] process(byte[] message) {
        return this.server.process(message);
    }

    private Message handle(Message requestMessage) {
        return mockHandle(requestMessage, this.stubs, this.invocations, this.random,
                this.server.uApiSchema, this.enableGeneratedDefaultStub, this.enableOptionalFieldGeneration,
                this.randomizeOptionalFieldGeneration);
    }
}
