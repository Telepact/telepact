package io.github.brenbar.uapi.internal;

import io.github.brenbar.uapi._RandomGenerator;

public class GenerateRandomNumber {
    static Object generateRandomNumber(Object blueprintValue, boolean useBlueprintValue,
            _RandomGenerator randomGenerator) {
        if (useBlueprintValue) {
            return blueprintValue;
        } else {
            return randomGenerator.nextDouble();
        }
    }
}
