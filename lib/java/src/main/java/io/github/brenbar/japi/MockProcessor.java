package io.github.brenbar.japi;

import java.util.Map;
import java.util.Random;

public class MockProcessor {

    public final Processor processor;
    private final Random random;

    public MockProcessor(String jApi) {
        this.processor = new Processor(jApi, this::handle);
        this.random = new Random();
    }

    public MockProcessor resetRandomSeed(Long seed) {
        this.random.setSeed(seed);
        return this;
    }

    public byte[] process(byte[] message) {
        return this.processor.process(message);
    }

    private Map<String, Object> handle(Context context, Map<String, Object> input) {
        return InternalMockProcess.handle(context, input, this.processor.jApi, this.random);
    }
}
