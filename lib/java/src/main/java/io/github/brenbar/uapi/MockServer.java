package io.github.brenbar.uapi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

import io.github.brenbar.uapi.internal._MockInvocation;
import io.github.brenbar.uapi.internal._MockStub;
import io.github.brenbar.uapi.internal._UMockCall;
import io.github.brenbar.uapi.internal._UMockStub;
import io.github.brenbar.uapi.internal._UType;

import static io.github.brenbar.uapi.internal.ExtendUApiSchema.extendUApiSchema;
import static io.github.brenbar.uapi.internal.GetMockUApiJson.getMockUApiJson;
import static io.github.brenbar.uapi.internal.MockHandle.mockHandle;

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
    private final _RandomGenerator random;
    private final boolean enableGeneratedDefaultStub;
    private final boolean enableOptionalFieldGeneration;
    private final boolean randomizeOptionalFieldGeneration;

    private final List<_MockStub> stubs = new ArrayList<>();
    private final List<_MockInvocation> invocations = new ArrayList<>();

    /**
     * Create a mock server with the given uAPI Schema.
     * 
     * @param uApiSchemaAsJson
     */
    public MockServer(UApiSchema uApiSchema, Options options) {
        this.random = new _RandomGenerator(options.generatedCollectionLengthMin, options.generatedCollectionLengthMax);
        this.enableGeneratedDefaultStub = options.enableMessageResponseGeneration;
        this.enableOptionalFieldGeneration = options.enableOptionalFieldGeneration;
        this.randomizeOptionalFieldGeneration = options.randomizeOptionalFieldGeneration;

        final var parsedTypes = new HashMap<String, _UType>();
        final var typeExtensions = new HashMap<String, _UType>();

        typeExtensions.put("_ext.Call_", new _UMockCall(parsedTypes));
        typeExtensions.put("_ext.Stub_", new _UMockStub(parsedTypes));

        final var combinedUApiSchema = extendUApiSchema(uApiSchema, getMockUApiJson(),
                typeExtensions);

        final var serverOptions = new Server.Options();
        serverOptions.onError = options.onError;
        serverOptions.authRequired = false;

        this.server = new Server(combinedUApiSchema, this::handle, serverOptions);

        final UApiSchema finalUApiSchema = this.server.uApiSchema;
        final Map<String, _UType> finalParsedUApiSchema = finalUApiSchema.parsed;

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
