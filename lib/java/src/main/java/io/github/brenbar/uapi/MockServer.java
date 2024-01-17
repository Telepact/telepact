package io.github.brenbar.uapi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

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

    private final List<_MockStub> stubs = new ArrayList<>();
    private final List<Invocation> invocations = new ArrayList<>();

    /**
     * Create a mock server with the given uAPI Schema.
     * 
     * @param uApiSchemaAsJson
     */
    public MockServer(UApiSchema uApiSchema, Options options) {
        this.random = new _RandomGenerator(options.generatedCollectionLengthMin, options.generatedCollectionLengthMax);
        this.enableGeneratedDefaultStub = options.enableMessageResponseGeneration;

        final var parsedTypes = new HashMap<String, _UType>();
        final var typeExtensions = new HashMap<String, _UType>();

        typeExtensions.put("_ext._Call", new _UMockCall(parsedTypes));
        typeExtensions.put("_ext._Stub", new _UMockStub(parsedTypes));

        final var combinedUApiSchema = UApiSchema.extendWithExtensions(uApiSchema, _InternalMockUApiUtil.getJson(),
                typeExtensions);

        final var serverOptions = new Server.Options();
        serverOptions.onError = options.onError;

        this.server = new Server(combinedUApiSchema, this::handle, serverOptions);

        final UApiSchema finalUApiSchema = server.uApiSchema;
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
        return _MockServerUtil.handle(requestMessage, this.stubs, this.invocations, this.random,
                this.server.uApiSchema, this.enableGeneratedDefaultStub);
    }
}
