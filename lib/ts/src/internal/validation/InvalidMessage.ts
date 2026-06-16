//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

export class InvalidMessage extends Error {
    constructor(cause?: Error) {
        super('Invalid message', {cause: cause});
    }
}
