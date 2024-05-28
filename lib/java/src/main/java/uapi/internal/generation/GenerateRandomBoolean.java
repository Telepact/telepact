package uapi.internal.generation;

import uapi.RandomGenerator;

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
