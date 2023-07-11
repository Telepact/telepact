package io.github.brenbar.japi;

import java.util.Map;

public class JApiFunction {
    public final String name;
    public final Map<String, Object> input;

    public JApiFunction(String name, Map<String, Object> input) {
        this.name = name;
        this.input = input;
    }
}
