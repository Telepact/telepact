//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

export class BinaryPackNode {
    public value: number;
    public nested: Map<number, BinaryPackNode>;

    constructor(value: number, nested: Map<number, BinaryPackNode>) {
        this.value = value;
        this.nested = nested;
    }
}
