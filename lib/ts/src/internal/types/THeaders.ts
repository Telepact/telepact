//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { TFieldDeclaration } from './TFieldDeclaration.js';

export class THeaders {
    name: string;
    requestHeaders: { [key: string]: TFieldDeclaration };
    responseHeaders: { [key: string]: TFieldDeclaration };

    constructor(
        name: string,
        requestHeaders: { [key: string]: TFieldDeclaration },
        responseHeaders: { [key: string]: TFieldDeclaration },
    ) {
        this.name = name;
        this.requestHeaders = requestHeaders;
        this.responseHeaders = responseHeaders;
    }
}
