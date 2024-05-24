package io.github.brenbar.uapi.internal;

import io.github.brenbar.uapi._RandomGenerator;

public class GenerateRandomBoolean {
    static Object generateRandomBoolean(Object blueprintValue, boolean useBlueprintValue,
            _RandomGenerator randomGenerator) {
        if (useBlueprintValue) {
            return blueprintValue;
        } else {
            return randomGenerator.nextBoolean();
        }
    }
}
