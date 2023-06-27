package io.github.brenbar.japi;

import java.util.Map;

public class MockProcessor {

    Processor processor;

    public MockProcessor(String jApi) {
        this.processor = new Processor(jApi, this::handle);
    }

    private Map<String, Object> handle(Context context, Map<String, Object> input) {
        return InternalMockProcess.handle(context, input, processor.jApi);
    }
}
