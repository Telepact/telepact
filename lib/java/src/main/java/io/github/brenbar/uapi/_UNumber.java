package io.github.brenbar.uapi;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

class _UNumber implements _UType {
    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<_ValidationFailure> validate(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        if (value instanceof BigInteger bi || value instanceof BigDecimal bd) {
            return List.of(
                    new _ValidationFailure(new ArrayList<Object>(), "NumberOutOfRange", Map.of()));
        } else if (value instanceof Number) {
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
            _RandomGenerator random) {
        if (useStartingValue) {
            return startingValue;
        } else {
            return random.nextDouble();
        }
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return "Number";
    }
}
