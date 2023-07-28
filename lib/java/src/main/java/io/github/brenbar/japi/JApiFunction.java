package io.github.brenbar.japi;

import java.util.Map;

public class JApiFunction {
    public final String name;
    public final Map<String, Object> argument;

    public JApiFunction(String name, Map<String, Object> argument) {
        this.name = name;
        this.argument = argument;
    }
}
