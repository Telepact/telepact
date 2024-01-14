package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;

public class SetExtension implements TypeExtension {

    @Override
    public List<ValidationFailure> validate(Object given, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics) {

        List<Object> value;
        try {
            value = _CastUtil.asList(given);
        } catch (ClassCastException e) {
            return _ValidateUtil.getTypeUnexpectedValidationFailure(List.of(), given, "Array");
        }

        if (typeParameters.size() != 1) {
            return List.of(new ValidationFailure(List.of(), "ExtensionValidationFailed",
                    Map.of("reason", "ExpectedOneGeneric")));
        }

        try {
            var test = new HashSet<>(value);
        } catch (Exception e) {
            return List.of(new ValidationFailure(List.of(), "ExtensionValidationFailed",
                    Map.of("reason", "SetHasDuplicates")));
        }

        var nestedType = typeParameters.get(0);

        var validationFailures = new ArrayList<ValidationFailure>();

        for (var e : value) {
            var nestedValidationFailures = nestedType.validate(e, generics);
            var newF = nestedValidationFailures.stream()
                    .map(f -> new ValidationFailure(_ValidateUtil.prepend(-1, f.path), f.reason, f.data)).toList();
            validationFailures.addAll(newF);
        }

        return validationFailures;
    }

}
