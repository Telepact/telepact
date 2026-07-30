//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { TUnion } from './TUnion.js';

export class TError {
    name: string;
    errors: TUnion;

    constructor(name: string, errors: TUnion) {
        this.name = name;
        this.errors = errors;
    }
}
