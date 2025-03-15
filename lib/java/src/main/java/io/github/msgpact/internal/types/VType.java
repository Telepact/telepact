package io.github.msgpact.internal.types;

import java.util.List;

import io.github.msgpact.internal.generation.GenerateContext;
import io.github.msgpact.internal.validation.ValidateContext;
import io.github.msgpact.internal.validation.ValidationFailure;

public interface VType {
        public int getTypeParameterCount();

        public List<ValidationFailure> validate(Object value,
                        List<VTypeDeclaration> typeParameters, ValidateContext ctx);

        public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
                        List<VTypeDeclaration> typeParameters, GenerateContext ctx);

        public String getName();
}
