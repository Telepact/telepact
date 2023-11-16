package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
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
        public Map<String, TypeExtension> typeExtensions = new HashMap<>();
        public boolean enableGeneratedDefaultStub = true;

        public Options setOnError(Consumer<Throwable> onError) {
            this.onError = onError;
            return this;
        }

        public Options addTypeExtension(String definitionKey, TypeExtension typeExtension) {
            this.typeExtensions.put(definitionKey, typeExtension);
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
    public MockServer(String jApiSchemaAsJson, Options options) {
        var combinedSchemaJson = InternalParse.combineJsonSchemas(List.of(
                jApiSchemaAsJson,
                InternalMockJApi.getJson()));

        var jApiSchemaCopy = new JApiSchema(new HashMap<>(), new HashMap<>());

        options.addTypeExtension("ext._Call", new MockCallTypeExtension(jApiSchemaCopy));
        options.addTypeExtension("ext._Stub", new MockStubTypeExtension(jApiSchemaCopy));

        this.server = new Server(combinedSchemaJson, this::handle,
                new Server.Options().setOnError(options.onError).setTypeExtensions(options.typeExtensions));

        jApiSchemaCopy.original.putAll(this.server.jApiSchema.original);
        jApiSchemaCopy.parsed.putAll(this.server.jApiSchema.parsed);

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
        return InternalMockServer.handle(requestMessage, this.stubs, this.invocations, this.random,
                this.server.jApiSchema, this.enableGeneratedDefaultStub);
    }
}
