package io.github.brenbar.uapi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.function.Consumer;

/**
 * A Mock instance of a uAPI server.
 * 
 * Clients can use this class as an alternative transport in their adapters to
 * interact with a functional uAPI with common mocking strategies.
 */
public class MockServer {

    public static class Options {
        public Consumer<Throwable> onError = (e) -> {
        };
        public boolean enableGeneratedDefaultStub = true;
        public int generatedCollectionLengthMin = 0;
        public int generatedCollectionLengthMax = 3;
    }

    private final Server server;
    private final RandomGenerator random;
    private final boolean enableGeneratedDefaultStub;

    private final List<_MockStub> stubs = new ArrayList<>();
    private final List<Invocation> invocations = new ArrayList<>();

    /**
     * Create a mock server with the given uAPI Schema.
     * 
     * @param uApiSchemaAsJson
     */
    public MockServer(UApiSchema uApiSchema, Options options) {
        var parsedTypes = new HashMap<String, _UType>();

        var typeExtensions = new HashMap<String, _UType>();
        typeExtensions.put("_ext._Call", new _UMockCall(parsedTypes));
        typeExtensions.put("_ext._Stub", new _UMockStub(parsedTypes));

        var combinedUApiSchema = UApiSchema.extendWithExtensions(uApiSchema, _InternalMockUApiUtil.getJson(),
                typeExtensions);

        this.server = new Server(combinedUApiSchema, this::handle,
                new Server.Options().setOnError(options.onError));

        parsedTypes.putAll(server.uApiSchema.parsed);

        this.random = new RandomGenerator(options.generatedCollectionLengthMin, options.generatedCollectionLengthMax);
        this.enableGeneratedDefaultStub = options.enableGeneratedDefaultStub;
    }

    /**
     * Set an alternative RNG seed to be used for stub data generation.
     * 
     * @param seed
     * @return
     */
    public MockServer resetRandomSeed(int seed) {
        this.random.setSeed(seed);
        return this;
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
