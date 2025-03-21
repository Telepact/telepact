package io.github.telepact.internal.mock;

import java.util.Map;

public class MockInvocation {
    public final String functionName;
    public final Map<String, Object> functionArgument;
    public boolean verified = false;

    public MockInvocation(String functionName, Map<String, Object> functionArgument) {
        this.functionName = functionName;
        this.functionArgument = functionArgument;
    }
}
