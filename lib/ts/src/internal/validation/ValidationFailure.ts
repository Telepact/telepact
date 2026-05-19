//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

export class ValidationFailure {
    constructor(
        public path: any[],
        public reason: string,
        public data: Record<string, any>,
    ) {}
}
