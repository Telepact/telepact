package io.github.brenbar.uapi.internal.generation;

import io.github.brenbar.uapi.RandomGenerator;

public class GenerateRandomString {
    public static Object generateRandomString(Object blueprintValue, boolean useBlueprintValue,
            RandomGenerator randomGenerator) {
        if (useBlueprintValue) {
            return blueprintValue;
        } else {
            return randomGenerator.nextString();
        }
    }
}
