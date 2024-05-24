package io.github.brenbar.uapi.internal;

import io.github.brenbar.uapi._RandomGenerator;

public class GenerateRandomString {
    static Object generateRandomString(Object blueprintValue, boolean useBlueprintValue,
            _RandomGenerator randomGenerator) {
        if (useBlueprintValue) {
            return blueprintValue;
        } else {
            return randomGenerator.nextString();
        }
    }
}
