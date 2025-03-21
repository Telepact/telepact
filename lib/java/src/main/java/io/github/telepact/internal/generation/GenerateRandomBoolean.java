package io.github.telepact.internal.generation;

public class GenerateRandomBoolean {
    public static Object generateRandomBoolean(Object blueprintValue, boolean useBlueprintValue, GenerateContext ctx) {
        if (useBlueprintValue) {
            return blueprintValue;
        } else {
            return ctx.randomGenerator.nextBoolean();
        }
    }
}
