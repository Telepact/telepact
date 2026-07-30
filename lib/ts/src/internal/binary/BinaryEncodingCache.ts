//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { BinaryEncoding } from "./BinaryEncoding.js";

export abstract class BinaryEncodingCache {
    abstract add(checksum: number, binaryEncodingMap: Map<string, number>): void
    abstract get(checksum: number): BinaryEncoding | undefined
    abstract remove(checksum: number): void
    abstract getChecksums(): number[];
}