package io.github.brenbar.japi.server;

import java.util.Map;

record Enum(String name, Map<String, Struct> cases) implements Type {
    @Override
    public String getName() {
        return name;
    }
}