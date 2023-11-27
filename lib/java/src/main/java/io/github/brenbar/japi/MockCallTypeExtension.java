package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class MockCallTypeExtension implements TypeExtension {

    public final JApiSchema jApiSchema;

    public MockCallTypeExtension(JApiSchema jApiSchema) {
        this.jApiSchema = jApiSchema;
    }

    @Override
    public List<ValidationFailure> validate(String path, Object givenObj) {
        var validationFailures = new ArrayList<ValidationFailure>();

        Map<String, Object> givenMap;
        try {
            givenMap = (Map<String, Object>) givenObj;

            var functionName = (String) null;
            for (var key : givenMap.keySet()) {
                if (key.startsWith("fn.")) {
                    functionName = key;
                    break;
                }
            }
            if (functionName == null) {
                validationFailures.add(new ValidationFailure(path, "InvalidCall"));
            }

            var input = (Map<String, Object>) givenMap.get(functionName);
            var functionDef = (Fn) this.jApiSchema.parsed.get(functionName);

            var inputFailures = InternalValidate.validateStructFields(path, functionDef.arg.fields, input);
            var failures = new ArrayList<ValidationFailure>();
            failures.addAll(inputFailures);

            var validFailures = new ArrayList<>();
            for (var inputFailure : failures) {
                if (inputFailure.reason.equals(ValidationErrorReasons.REQUIRED_STRUCT_FIELD_MISSING)) {
                    continue;
                }
                validFailures.add(inputFailure);
            }

        } catch (ClassCastException e) {
            validationFailures.add(new ValidationFailure(path, "CallTypeRequired"));
        }

        return validationFailures;
    }

}
