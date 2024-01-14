package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.List;

public class _UArray implements _UType {

    @Override
    public int getTypeParameterCount() {
        return 1;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        if (value instanceof List l) {
            var nestedTypeDeclaration = typeParameters.get(0);
            var validationFailures = new ArrayList<ValidationFailure>();
            for (var i = 0; i < l.size(); i += 1) {
                var element = l.get(i);
                var nestedValidationFailures = nestedTypeDeclaration.validate(element, generics);
                final var index = i;
                var nestedValidationFailuresWithPath = nestedValidationFailures
                        .stream()
                        .map(f -> new ValidationFailure(_ValidateUtil.prepend(index, f.path), f.reason,
                                f.data))
                        .toList();
                validationFailures.addAll(nestedValidationFailuresWithPath);
            }
            return validationFailures;
        } else {
            return _ValidateUtil.getTypeUnexpectedValidationFailure(List.of(), value,
                    this.getName(generics));
        }
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            RandomGenerator random) {
        var nestedTypeDeclaration = typeParameters.get(0);
        if (useStartingValue) {
            var startingArray = (List<Object>) startingValue;
            var array = new ArrayList<Object>();
            for (var startingArrayValue : startingArray) {
                var value = nestedTypeDeclaration.generateRandomValue(startingArrayValue, true,
                        includeRandomOptionalFields, generics, random);
                array.add(value);
            }
            return array;
        } else {
            var length = random.nextCollectionLength();
            var array = new ArrayList<Object>();
            for (int i = 0; i < length; i += 1) {
                var value = nestedTypeDeclaration.generateRandomValue(null, false,
                        includeRandomOptionalFields,
                        generics, random);
                array.add(value);
            }
            return array;
        }
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return "Array";
    }
}
