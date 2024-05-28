package uapi.internal.generation;

import uapi.RandomGenerator;

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
