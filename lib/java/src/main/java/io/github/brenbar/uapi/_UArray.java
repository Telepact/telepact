package io.github.brenbar.uapi;

import java.util.ArrayList;
import java.util.List;

class _UArray implements _UType {

    @Override
    public int getTypeParameterCount() {
        return 1;
    }

    @Override
    public List<_ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        if (value instanceof final List l) {
            final var nestedTypeDeclaration = typeParameters.get(0);

            final var validationFailures = new ArrayList<_ValidationFailure>();
            for (var i = 0; i < l.size(); i += 1) {
                final var element = l.get(i);
                final var nestedValidationFailures = nestedTypeDeclaration.validate(element, generics);
                final var index = i;

                final var nestedValidationFailuresWithPath = new ArrayList<_ValidationFailure>();
                for (var f : nestedValidationFailures) {
                    final List<Object> finalPath = _ValidateUtil.prepend(index, f.path);
                    nestedValidationFailuresWithPath.add(new _ValidationFailure(finalPath, f.reason,
                            f.data));
                }

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
            _RandomGenerator randomGenerator) {
        final var nestedTypeDeclaration = typeParameters.get(0);

        if (useStartingValue) {
            final var startingArray = (List<Object>) startingValue;

            final var array = new ArrayList<Object>();
            for (final var startingArrayValue : startingArray) {
                final var value = nestedTypeDeclaration.generateRandomValue(startingArrayValue, true,
                        includeRandomOptionalFields, generics, randomGenerator);

                array.add(value);
            }

            return array;
        } else {
            final var length = randomGenerator.nextCollectionLength();

            final var array = new ArrayList<Object>();
            for (int i = 0; i < length; i += 1) {
                final var value = nestedTypeDeclaration.generateRandomValue(null, false,
                        includeRandomOptionalFields,
                        generics, randomGenerator);

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
