package uapi.internal.generation;

import uapi.RandomGenerator;

public class GenerateRandomInteger {
    public static Object generateRandomInteger(Object blueprintValue, boolean useBlueprintValue,
            RandomGenerator randomGenerator) {
        if (useBlueprintValue) {
            return blueprintValue;
        } else {
            return randomGenerator.nextInt();
        }
    }
}
