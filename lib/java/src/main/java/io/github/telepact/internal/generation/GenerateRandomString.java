//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.generation;

public class GenerateRandomString {
    public static Object generateRandomString(Object blueprintValue, boolean useBlueprintValue,
            GenerateContext ctx) {
        if (useBlueprintValue) {
            return blueprintValue;
        } else {
            return ctx.randomGenerator.nextString();
        }
    }
}
