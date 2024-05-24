package io.github.brenbar.uapi.internal;

import io.github.brenbar.uapi.RandomGenerator;

public class GenerateRandomBoolean {
    public static Object generateRandomBoolean(Object blueprintValue, boolean useBlueprintValue,
            RandomGenerator randomGenerator) {
        if (useBlueprintValue) {
            return blueprintValue;
        } else {
            return randomGenerator.nextBoolean();
        }
    }
}
