package io.github.brenbar.uapi;

import java.util.List;

class _UAny implements _UType {

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        return List.of();
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator random) {
        final var selectType = random.nextInt(3);
        if (selectType == 0) {
            return random.nextBoolean();
        } else if (selectType == 1) {
            return random.nextInt();
        } else {
            return random.nextString();
        }
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return "Any";
    }
}
