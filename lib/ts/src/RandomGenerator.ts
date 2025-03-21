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

/*
 * For debeugging.
 */
function findStack() {
    const e = new Error();
    const stack = e.stack.split('\n');
    for (let i = 3; i < stack.length; i += 1) {
        const line = stack[i].split('(')[0];
        if (!line.includes('RandomGenerator')) {
            return line + stack[i - 1].split('(')[0];
        }
    }
    throw new Error();
}

export class RandomGenerator {
    seed: number;
    private collectionLengthMin: number;
    private collectionLengthMax: number;
    private count: number = 0;

    constructor(collectionLengthMin: number, collectionLengthMax: number) {
        this.setSeed(0);
        this.collectionLengthMin = collectionLengthMin;
        this.collectionLengthMax = collectionLengthMax;
    }

    setSeed(seed: number): void {
        this.seed = seed === 0 ? 1 : seed;
    }

    nextInt(): number {
        let x = this.seed;
        x ^= x << 16;
        x ^= x >> 11;
        x ^= x << 5;
        this.seed = x === 0 ? 1 : x;
        this.count += 1;
        const result = this.seed;
        // console.log(`${this.count} ${result} ${findStack()}`);
        return result & 0x7fffffff;
    }

    nextIntWithCeiling(ceiling: number): number {
        if (ceiling === 0) {
            return 0;
        }
        return this.nextInt() % ceiling;
    }

    nextBoolean(): boolean {
        return this.nextIntWithCeiling(31) > 15;
    }

    nextString(): string {
        const buffer = new ArrayBuffer(4);
        const view = new DataView(buffer);
        view.setInt32(0, this.nextInt());

        const byteArray = new Uint8Array(buffer);
        const base64String = btoa(String.fromCharCode.apply(null, byteArray));
        return base64String.replace(/=/g, '');
    }

    nextDouble(): number {
        return (this.nextInt() & 0x7fffffff) / 0x7fffffff;
    }

    nextCollectionLength(): number {
        return this.nextIntWithCeiling(this.collectionLengthMax - this.collectionLengthMin) + this.collectionLengthMin;
    }
}
