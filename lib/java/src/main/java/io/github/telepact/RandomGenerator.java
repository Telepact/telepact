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

package io.github.telepact;

import java.nio.ByteBuffer;
import java.util.Base64;

public class RandomGenerator {
    int seed = 0;
    private int collectionLengthMin;
    private int collectionLengthMax;
    private int count = 0;

    public RandomGenerator(int collectionLengthMin, int collectionLengthMax) {
        this.setSeed(0);
        this.collectionLengthMin = collectionLengthMin;
        this.collectionLengthMax = collectionLengthMax;
    }

    public void setSeed(int seed) {
        this.seed = seed == 0 ? 1 : seed;
    }

    private static String findStack() {
        var i = 0;
        for (var stack : Thread.currentThread().getStackTrace()) {
            i += 1;
            if (i == 1) {
                continue;
            }
            var stackStr = String.valueOf(stack);
            if (!stackStr.contains("_RandomGenerator")) {
                return stackStr;
            }
        }
        throw new RuntimeException();
    }

    public int nextInt() {
        var x = this.seed;
        x ^= x << 16;
        x ^= x >> 11;
        x ^= x << 5;
        this.seed = seed == 0 ? 1 : x;
        this.count += 1;
        var result = this.seed;
        // System.out.println("%d %d %s".formatted(count, result, findStack()));
        return result & 0x7fffffff;
    }

    public int nextIntWithCeiling(int ceiling) {
        if (ceiling == 0) {
            return 0;
        }
        return (int) nextInt() % ceiling;
    }

    public boolean nextBoolean() {
        return nextIntWithCeiling(31) > 15;
    }
    
    public byte[] nextBytes() {
        var bytes = ByteBuffer.allocate(Integer.BYTES);
        bytes.putInt(nextInt());
        return bytes.array();
    }

    public String nextString() {
        var bytes = nextBytes();
        return Base64.getEncoder().withoutPadding().encodeToString(bytes);
    }

    public double nextDouble() {
        return ((double) (nextInt() & 0x7fffffff) / ((double) 0x7fffffff));
    }

    public int nextCollectionLength() {
        return nextIntWithCeiling(this.collectionLengthMax - this.collectionLengthMin) + this.collectionLengthMin;
    }
}
