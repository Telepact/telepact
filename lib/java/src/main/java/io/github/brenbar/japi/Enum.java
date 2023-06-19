package io.github.brenbar.japi;

import java.util.Map;

record Enum(String name, Map<String, Struct> cases) implements Type {
    @Override
    public String getName() {
        return name;
    }
}