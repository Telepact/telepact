package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.function.Consumer;

/**
 * A Mock instance of a jAPI server.
 * 
 * Clients can use this class as an alternative transport in their adapters to
 * interact with a functional jAPI with common mocking strategies.
 */
public class MockServer {

    public static class Options {
        public Consumer<Throwable> onError = (e) -> {
        };
        public boolean enableGeneratedDefaultStub = true;
        public int generatedCollectionLengthMin = 0;
        public int generatedCollectionLengthMax = 3;
    }

    public final Server server;
    private final RandomGenerator random;
    private final boolean enableGeneratedDefaultStub;

    private final List<MockStub> stubs = new ArrayList<>();
    private final List<Invocation> invocations = new ArrayList<>();

    /**
     * Create a mock server with the given jAPI Schema.
     * 
     * @param jApiSchemaAsJson
     */
    public MockServer(JApiSchema jApiSchema, Options options) {
        var parsedTypes = new HashMap<String, UType>();

        var typeExtensions = new HashMap<String, UType>();
        typeExtensions.put("_ext._Call", new MockCallTypeExtension(parsedTypes));
        typeExtensions.put("_ext._Stub", new MockStubTypeExtension(parsedTypes));

        var combinedJApiSchema = JApiSchema.extend(jApiSchema, _InternalMockJApiUtil.getJson(), typeExtensions);

        this.server = new Server(combinedJApiSchema, this::handle,
                new Server.Options().setOnError(options.onError));

        parsedTypes.putAll(server.jApiSchema.parsed);

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
     * Process a given jAPI Request Message into a jAPI Response Message.
     * 
     * @param requestMessageBytes
     * @return
     */
    public byte[] process(byte[] message) {
        return this.server.process(message);
    }

    private Message handle(Message requestMessage) {
        return _MockServerUtil.handle(requestMessage, this.stubs, this.invocations, this.random,
                this.server.jApiSchema, this.enableGeneratedDefaultStub);
    }
}
