export class BinaryPackNode {
    value: number;
    nested: Map<number, BinaryPackNode>;

    constructor(value: number, nested: Map<number, BinaryPackNode>) {
        this.value = value;
        this.nested = nested;
    }
}
