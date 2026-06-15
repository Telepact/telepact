//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

export abstract class Base64Encoder {
    abstract encode(message: object[]): object[];
    abstract decode(message: object[]): object[];
}