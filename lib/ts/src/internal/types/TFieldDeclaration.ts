//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { TTypeDeclaration } from './TTypeDeclaration.js';

export class TFieldDeclaration {
    fieldName: string;
    typeDeclaration: TTypeDeclaration;
    optional: boolean;

    constructor(fieldName: string, typeDeclaration: TTypeDeclaration, optional: boolean) {
        this.fieldName = fieldName;
        this.typeDeclaration = typeDeclaration;
        this.optional = optional;
    }
}
