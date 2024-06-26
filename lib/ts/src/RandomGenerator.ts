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
        this.seed = (seed & 0x7ffffffe) + 1;
    }

    nextInt(): number {
        let x = this.seed;
        x ^= x << 13;
        x ^= x >> 17;
        x ^= x << 5;
        this.seed = (x & 0x7ffffffe) + 1;
        this.count += 1;
        const result = this.seed;
        console.log(`${this.count} ${result} ${findStack()}`);
        return result;
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
