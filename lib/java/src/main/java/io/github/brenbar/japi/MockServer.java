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

        public Options setOnError(Consumer<Throwable> onError) {
            this.onError = onError;
            return this;
        }

        public Options setEnableGeneratedDefaultStub(boolean enableGeneratedDefaultStub) {
            this.enableGeneratedDefaultStub = enableGeneratedDefaultStub;
            return this;
        }

    }

    public final Server server;
    private final MockRandom random;
    private boolean enableGeneratedDefaultStub;

    private final List<MockStub> stubs = new ArrayList<>();
    private final List<Invocation> invocations = new ArrayList<>();

    /**
     * Create a mock server with the given jAPI Schema.
     * 
     * @param jApiSchemaAsJson
     */
    public MockServer(JApiSchema jApiSchema, Options options) {
        var parsedTypes = new HashMap<String, Type>();

        var typeExtensions = new HashMap<String, TypeExtension>();
        typeExtensions.put("ext._Call", new MockCallTypeExtension(parsedTypes));
        typeExtensions.put("ext._Stub", new MockStubTypeExtension(parsedTypes));

        var mockJApiSchema = new JApiSchema(_InternalMockJApiUtil.getJson(), typeExtensions);
        var combinedJApiSchema = new JApiSchema(jApiSchema, mockJApiSchema);

        this.server = new Server(combinedJApiSchema, this::handle,
                new Server.Options().setOnError(options.onError));

        parsedTypes.putAll(server.jApiSchema.parsed);

        this.random = new MockRandom();
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
     * Set an error handler to run on every error that occurs during request
     * processing.
     * 
     * @param onError
     * @return
     */
    public MockServer setOnError(Consumer<Throwable> onError) {
        this.server.onError = onError;
        return this;
    }

    public MockServer setEnableGeneratedDefaultStub(boolean enableGeneratedDefaultStub) {
        this.enableGeneratedDefaultStub = enableGeneratedDefaultStub;
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
