//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { Parser } from 'prettier';

declare module 'prettier-plugin-telepact' {
    const languages: any[];
    const parsers: { [key: string]: Parser };
    const printers: { [key: string]: any };
}
