package io.github.brenbar.uapi.internal;

import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi.RandomGenerator;

public interface UType {
        public int getTypeParameterCount();

        public List<ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
                        List<UTypeDeclaration> typeParameters,
                        List<UTypeDeclaration> generics);

        public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
                        boolean includeOptionalFields, boolean randomizeOptionalFields,
                        List<UTypeDeclaration> typeParameters,
                        List<UTypeDeclaration> generics,
                        RandomGenerator randomGenerator);

        public String getName(List<UTypeDeclaration> generics);
}
