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

/**
 * A utility class for generating random values.
 */
public class RandomGenerator {
    int seed = 0;
    private int collectionLengthMin;
    private int collectionLengthMax;
    private int count = 0;

    /**
     * Constructs a RandomGenerator with specified collection length bounds.
     *
     * @param collectionLengthMin the minimum collection length
     * @param collectionLengthMax the maximum collection length
     */
    public RandomGenerator(int collectionLengthMin, int collectionLengthMax) {
        this.setSeed(0);
        this.collectionLengthMin = collectionLengthMin;
        this.collectionLengthMax = collectionLengthMax;
    }

    /**
     * Sets the seed for the random generator.
     *
     * @param seed the seed value
     */
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

    /**
     * Generates a random integer.
     *
     * @return a random integer
     */
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

    /**
     * Generates a random integer with an upper ceiling.
     *
     * @param ceiling the upper limit (exclusive)
     * @return a random integer
     */
    public int nextIntWithCeiling(int ceiling) {
        if (ceiling == 0) {
            return 0;
        }
        return (int) nextInt() % ceiling;
    }

    /**
     * Generates a random double.
     *
     * @return a random double
     */
    public double nextDouble() {
        return ((double) (nextInt() & 0x7fffffff) / ((double) 0x7fffffff));
    }

    /**
     * Generates a random boolean.
     *
     * @return a random boolean
     */
    public boolean nextBoolean() {
        return nextIntWithCeiling(31) > 15;
    }
    
    /**
     * Generates a random byte array.
     *
     * @return a random byte array
     */
    public byte[] nextBytes() {
        var bytes = ByteBuffer.allocate(Integer.BYTES);
        bytes.putInt(nextInt());
        return bytes.array();
    }

    /**
     * Generates a random string.
     *
     * @return a random string
     */
    public String nextString() {
        var bytes = nextBytes();
        return Base64.getEncoder().withoutPadding().encodeToString(bytes);
    }

    /**
     * Generates a random collection length within the specified bounds.
     *
     * @return a random collection length
     */
    public int nextCollectionLength() {
        return nextIntWithCeiling(this.collectionLengthMax - this.collectionLengthMin) + this.collectionLengthMin;
    }
}
