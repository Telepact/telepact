//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

package io.github.telepact.internal.generation;

public class GenerateRandomAny {
    public static Object generateRandomAny(GenerateContext ctx) {
        final var selectType = ctx.randomGenerator.nextIntWithCeiling(3);
        if (selectType == 0) {
            return ctx.randomGenerator.nextBoolean();
        } else if (selectType == 1) {
            return ctx.randomGenerator.nextInt();
        } else {
            return ctx.randomGenerator.nextString();
        }
    }
}
