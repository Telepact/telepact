package io.github.brenbar.japi;

import java.util.List;

class _UBoolean implements _UType {

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        if (value instanceof Boolean) {
            return List.of();
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
        if (useStartingValue) {
            return startingValue;
        } else {
            return random.nextBoolean();
        }
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return "Boolean";
    }

}
