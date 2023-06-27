package io.github.brenbar.japi;

import java.util.Map;
import java.util.Random;

public class MockProcessor {

    Processor processor;
    Random random;

    public MockProcessor(String jApi) {
        this.processor = new Processor(jApi, this::handle);
    }

    public MockProcessor resetRandomSeed(Long seed) {
        this.random.setSeed(seed);
        return this;
    }

    private Map<String, Object> handle(Context context, Map<String, Object> input) {
        return InternalMockProcess.handle(context, input, this.processor.jApi, this.random);
    }
}
