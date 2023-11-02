package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class MockStubTypeExtension implements TypeExtension {

    private JApiSchema jApiSchema;

    public MockStubTypeExtension(JApiSchema jApiSchema) {
        this.jApiSchema = jApiSchema;
    }

    @Override
    public String getName() {
        return "ext._Stub";
    }

    @Override
    public List<ValidationFailure> validate(String path, Map<String, Object> given) {

        var validationFailures = new ArrayList<ValidationFailure>();

        if (!given.containsKey("->")) {
            validationFailures.add(new ValidationFailure(path, "StubMissingOutput"));
        }

        var functionName = (String) null;
        for (var key : given.keySet()) {
            if (key.startsWith("fn.")) {
                functionName = key;
                break;
            }
        }
        if (functionName == null) {
            validationFailures.add(new ValidationFailure(path, "StubMissingCall"));
        }

        var call = given.get(functionName);
        var functionDef = this.jApiSchema.parsed.get(functionName);

        InternalServer.validateStruct(path, null, given)

        return validationFailures;
    }

}
