package uapi.internal.generation;

import java.util.List;

import uapi.RandomGenerator;
import uapi.internal.types.UTypeDeclaration;

public class GenerateContext {
    Object blueprintValue;
    boolean useBlueprintValue;
    boolean includeOptionalFields;
    boolean randomizeOptionalFields;
    boolean alwaysIncludeRequiredFields;
    List<UTypeDeclaration> typeParameters;
    String fnScope;
    RandomGenerator randomGenerator;

    public GenerateContext(Object blueprintValue, boolean useBlueprintValue, boolean includeOptionalFields,
            boolean randomizeOptionalFields, boolean alwaysIncludeRequiredFields, List<UTypeDeclaration> typeParameters,
            String fnScope, RandomGenerator randomGenerator) {
        this.blueprintValue = blueprintValue;
        this.useBlueprintValue = useBlueprintValue;
        this.includeOptionalFields = includeOptionalFields;
        this.randomizeOptionalFields = randomizeOptionalFields;
        this.alwaysIncludeRequiredFields = alwaysIncludeRequiredFields;
        this.typeParameters = typeParameters;
        this.fnScope = fnScope;
        this.randomGenerator = randomGenerator;
    }

    public GenerateContext copyWithNewBlueprintValue(Object blueprintValue) {
        return new GenerateContext(blueprintValue, useBlueprintValue, includeOptionalFields, randomizeOptionalFields,
                alwaysIncludeRequiredFields, typeParameters, fnScope, randomGenerator);
    }

    public GenerateContext copyWithNewBlueprintValueAndUseBlueprintValue(Object blueprintValue,
            boolean useBlueprintValue) {
        return new GenerateContext(blueprintValue, useBlueprintValue, includeOptionalFields, randomizeOptionalFields,
                alwaysIncludeRequiredFields, typeParameters, fnScope, randomGenerator);
    }

    public GenerateContext copyWithNewTypeParameters(List<UTypeDeclaration> typeParameters) {
        return new GenerateContext(blueprintValue, useBlueprintValue, includeOptionalFields, randomizeOptionalFields,
                alwaysIncludeRequiredFields, typeParameters, fnScope, randomGenerator);
    }

    public GenerateContext copyWithNewAlwaysIncludeRequiredFields(boolean alwaysIncludeRequiredFields) {
        return new GenerateContext(blueprintValue, useBlueprintValue, includeOptionalFields, randomizeOptionalFields,
                alwaysIncludeRequiredFields, typeParameters, fnScope, randomGenerator);
    }
}