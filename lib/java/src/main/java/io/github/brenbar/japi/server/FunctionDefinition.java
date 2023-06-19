package io.github.brenbar.japi.server;

import java.util.List;

record FunctionDefinition(
        String name,
        Struct inputStruct,
        Struct outputStruct,
        List<String> errors) implements Definition {
    @Override
    public String getName() {
        return name;
    }
}
