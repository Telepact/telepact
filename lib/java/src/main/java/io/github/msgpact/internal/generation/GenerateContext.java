package io.github.msgpact.internal.generation;

import io.github.msgpact.RandomGenerator;

public class GenerateContext {
    public final boolean includeOptionalFields;
    public final boolean randomizeOptionalFields;
    public final boolean alwaysIncludeRequiredFields;
    public final String fnScope;
    public final RandomGenerator randomGenerator;

    public GenerateContext(boolean includeOptionalFields,
            boolean randomizeOptionalFields, boolean alwaysIncludeRequiredFields,
            String fnScope, RandomGenerator randomGenerator) {
        this.includeOptionalFields = includeOptionalFields;
        this.randomizeOptionalFields = randomizeOptionalFields;
        this.alwaysIncludeRequiredFields = alwaysIncludeRequiredFields;
        this.fnScope = fnScope;
        this.randomGenerator = randomGenerator;
    }

    public GenerateContext copyWithNewAlwaysIncludeRequiredFields(boolean alwaysIncludeRequiredFields) {
        return new GenerateContext(includeOptionalFields, randomizeOptionalFields,
                alwaysIncludeRequiredFields, fnScope, randomGenerator);
    }
}