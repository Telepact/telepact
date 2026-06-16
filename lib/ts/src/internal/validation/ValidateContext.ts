//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

export class ValidateContext {
    path: string[];
    select: { [key: string]: any } | null;
    fn: string | null;
    coerceBase64: boolean;
    base64Coercions: Record<string, object>;
    bytesCoercions: Record<string, object>;

    constructor(
        select: { [key: string]: any } | null, 
        fn: string | null, 
        coerceBase64: boolean,
    ) {
        this.path = [];
        this.select = select;
        this.fn = fn;
        this.coerceBase64 = coerceBase64;
        this.base64Coercions = {};
        this.bytesCoercions = {};
    }
}
