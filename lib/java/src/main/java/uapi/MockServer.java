package uapi;

import static uapi.internal.mock.MockHandle.mockHandle;
import static uapi.internal.schema.ExtendUApiSchema.extendUApiSchema;
import static uapi.internal.schema.GetMockUApiJson.getMockUApiJson;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

import uapi.internal.mock.MockInvocation;
import uapi.internal.mock.MockStub;
import uapi.internal.types.UMockCall;
import uapi.internal.types.UMockStub;
import uapi.internal.types.UType;

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
    public MockServer(UApiSchema uApiSchema, Options options) {
        this.random = new RandomGenerator(options.generatedCollectionLengthMin, options.generatedCollectionLengthMax);
        this.enableGeneratedDefaultStub = options.enableMessageResponseGeneration;
        this.enableOptionalFieldGeneration = options.enableOptionalFieldGeneration;
        this.randomizeOptionalFieldGeneration = options.randomizeOptionalFieldGeneration;

        final var parsedTypes = new HashMap<String, UType>();
        final var typeExtensions = new HashMap<String, UType>();

        typeExtensions.put("_ext.Call_", new UMockCall(parsedTypes));
        typeExtensions.put("_ext.Stub_", new UMockStub(parsedTypes));

        final var combinedUApiSchema = extendUApiSchema(uApiSchema, getMockUApiJson(),
                typeExtensions);

        final var serverOptions = new Server.Options();
        serverOptions.onError = options.onError;
        serverOptions.authRequired = false;

        this.server = new Server(combinedUApiSchema, this::handle, serverOptions);

        final UApiSchema finalUApiSchema = this.server.uApiSchema;
        final Map<String, UType> finalParsedUApiSchema = finalUApiSchema.parsed;

        parsedTypes.putAll(finalParsedUApiSchema);
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
