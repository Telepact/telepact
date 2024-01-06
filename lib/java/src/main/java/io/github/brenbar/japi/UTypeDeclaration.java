package io.github.brenbar.japi;

import java.util.Collections;
import java.util.List;

public class UTypeDeclaration {
    public final UType type;
    public final boolean nullable;
    public final List<UTypeDeclaration> typeParameters;

    public UTypeDeclaration(
            UType type,
            boolean nullable, List<UTypeDeclaration> typeParameters) {
        this.type = type;
        this.nullable = nullable;
        this.typeParameters = typeParameters;
    }

    public List<ValidationFailure> validate(Object value, List<UTypeDeclaration> generics) {
        if (value == null) {
            var isNullable = this.type instanceof UGeneric g
                    ? generics.get(g.index).nullable
                    : this.nullable;
            if (!isNullable) {
                return _ValidateUtil.getTypeUnexpectedValidationFailure(List.of(), value,
                        this.type.getName(generics));
            } else {
                return Collections.emptyList();
            }
        } else {
            return this.type.validate(value, this.typeParameters, generics);
        }
    }

    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<UTypeDeclaration> generics,
            RandomGenerator random) {
        if (this.nullable && !useStartingValue && random.nextBoolean()) {
            return null;
        } else {
            return this.type.generateRandomValue(startingValue, useStartingValue, includeRandomOptionalFields,
                    this.typeParameters, generics, random);
        }
    }
}
