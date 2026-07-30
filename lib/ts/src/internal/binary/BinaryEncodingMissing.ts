//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

export class BinaryEncodingMissing extends Error {
    constructor(key: object) {
        super(`Missing binary encoding for ${String(key)}`);
    }
}
