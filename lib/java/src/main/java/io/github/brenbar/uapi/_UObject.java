package io.github.brenbar.uapi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

class _UObject implements _UType {

    @Override
    public int getTypeParameterCount() {
        return 1;
    }

    @Override
    public List<_ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        if (value instanceof final Map<?, ?> m) {
            final var nestedTypeDeclaration = typeParameters.get(0);

            final var validationFailures = new ArrayList<_ValidationFailure>();
            for (Map.Entry<?, ?> entry : m.entrySet()) {
                final var k = (String) entry.getKey();
                final var v = entry.getValue();
                final var nestedValidationFailures = nestedTypeDeclaration.validate(v, generics);

                final var nestedValidationFailuresWithPath = new ArrayList<_ValidationFailure>();
                for (var f : nestedValidationFailures) {
                    final List<Object> thisPath = _ValidateUtil.prepend(k, f.path);

                    nestedValidationFailuresWithPath.add(new _ValidationFailure(thisPath, f.reason, f.data));
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
            _RandomGenerator random) {
        final var nestedTypeDeclaration = typeParameters.get(0);

        if (useStartingValue) {
            final var startingObj = (Map<String, Object>) startingValue;

            final var obj = new TreeMap<String, Object>();
            for (final var startingObjEntry : startingObj.entrySet()) {
                final var key = startingObjEntry.getKey();
                final var startingObjValue = startingObjEntry.getValue();
                final var value = nestedTypeDeclaration.generateRandomValue(startingObjValue, true,
                        includeRandomOptionalFields, generics, random);
                obj.put(key, value);
            }

            return obj;
        } else {
            final var length = random.nextCollectionLength();

            final var obj = new TreeMap<String, Object>();
            for (int i = 0; i < length; i += 1) {
                final var key = random.nextString();
                final var value = nestedTypeDeclaration.generateRandomValue(null, false, includeRandomOptionalFields,
                        generics, random);
                obj.put(key, value);
            }

            return obj;
        }
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return "Object";
    }

}
