package io.github.brenbar.uapi.internal;

import io.github.brenbar.uapi.RandomGenerator;

public class GenerateRandomInteger {
    static Object generateRandomInteger(Object blueprintValue, boolean useBlueprintValue,
            RandomGenerator randomGenerator) {
        if (useBlueprintValue) {
            return blueprintValue;
        } else {
            return randomGenerator.nextInt();
        }
    }
}
