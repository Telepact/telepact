package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class MockStubTypeExtension implements TypeExtension {

    public final JApiSchema jApiSchema;

    public MockStubTypeExtension(JApiSchema jApiSchema) {
        this.jApiSchema = jApiSchema;
    }

    @Override
    public List<ValidationFailure> validate(String path, Object givenObj) {
        var validationFailures = new ArrayList<ValidationFailure>();

        Map<String, Object> givenMap;
        try {
            givenMap = (Map<String, Object>) givenObj;

            if (!givenMap.containsKey("->")) {
                validationFailures.add(new ValidationFailure(path, "StubMissingResult"));
            }

            var functionName = (String) null;
            for (var key : givenMap.keySet()) {
                if (key.startsWith("fn.")) {
                    functionName = key;
                    break;
                }
            }
            if (functionName == null) {
                validationFailures.add(new ValidationFailure(path, "StubMissingCall"));
            }

            var input = (Map<String, Object>) givenMap.get(functionName);
            var output = (Map<String, Object>) givenMap.get("->");
            var functionDef = (Fn) this.jApiSchema.parsed.get(functionName);

            var inputFailures = InternalServer.validateStruct(path, functionDef.arg.fields, input);
            var outputFailures = InternalServer.validateEnum(path, functionDef.result.values, output);
            var failures = new ArrayList<ValidationFailure>();
            failures.addAll(inputFailures);
            failures.addAll(outputFailures);

            var validFailures = new ArrayList<>();
            for (var inputFailure : failures) {
                if (inputFailure.reason.equals(ValidationErrorReasons.REQUIRED_STRUCT_FIELD_MISSING)) {
                    continue;
                }
                validFailures.add(inputFailure);
            }

        } catch (ClassCastException e) {
            validationFailures.add(new ValidationFailure(path, "StubTypeRequired"));
        }

        return validationFailures;
    }

}
