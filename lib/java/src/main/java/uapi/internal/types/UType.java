package uapi.internal.types;

import java.util.List;
import java.util.Map;

import uapi.RandomGenerator;
import uapi.internal.validation.ValidationFailure;

public interface UType {
        public int getTypeParameterCount();

        public List<ValidationFailure> validate(Object value, Map<String, Object> select, String fn,
                        List<UTypeDeclaration> typeParameters);

        public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
                        boolean includeOptionalFields, boolean randomizeOptionalFields,
                        List<UTypeDeclaration> typeParameters,
                        RandomGenerator randomGenerator);

        public String getName();
}
