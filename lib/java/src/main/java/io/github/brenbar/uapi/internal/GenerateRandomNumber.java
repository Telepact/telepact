package io.github.brenbar.uapi.internal;

import io.github.brenbar.uapi.RandomGenerator;

public class GenerateRandomNumber {
    public static Object generateRandomNumber(Object blueprintValue, boolean useBlueprintValue,
            RandomGenerator randomGenerator) {
        if (useBlueprintValue) {
            return blueprintValue;
        } else {
            return randomGenerator.nextDouble();
        }
    }
}
