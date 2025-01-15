package uapi.internal.generation;

import java.util.List;

import uapi.RandomGenerator;
import uapi.internal.types.UTypeDeclaration;

public class GenerateContext {
    Object blueprintValue;
    boolean useBlueprintValue;
    boolean includeOptionalFields;
    boolean randomizeOptionalFields;
    List<UTypeDeclaration> typeParameters;
    RandomGenerator randomGenerator;

    public GenerateContext(Object blueprintValue, boolean useBlueprintValue, boolean includeOptionalFields,
            boolean randomizeOptionalFields, List<UTypeDeclaration> typeParameters, RandomGenerator randomGenerator) {
        this.blueprintValue = blueprintValue;
        this.useBlueprintValue = useBlueprintValue;
        this.includeOptionalFields = includeOptionalFields;
        this.randomizeOptionalFields = randomizeOptionalFields;
        this.typeParameters = typeParameters;
        this.randomGenerator = randomGenerator;
    }

    public GenerateContext copyWithNewBlueprintValue(Object blueprintValue) {
        return new GenerateContext(blueprintValue, useBlueprintValue, includeOptionalFields, randomizeOptionalFields,
                typeParameters, randomGenerator);
    }

    public GenerateContext copyWithNewBlueprintValueAndUseBlueprintValue(Object blueprintValue,
            boolean useBlueprintValue) {
        return new GenerateContext(blueprintValue, useBlueprintValue, includeOptionalFields, randomizeOptionalFields,
                typeParameters, randomGenerator);
    }

    public GenerateContext copyWithNewTypeParameters(List<UTypeDeclaration> typeParameters) {
        return new GenerateContext(blueprintValue, useBlueprintValue, includeOptionalFields, randomizeOptionalFields,
                typeParameters, randomGenerator);
    }
}