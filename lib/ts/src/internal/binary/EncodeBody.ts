//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { BinaryEncoding } from '../../internal/binary/BinaryEncoding.js';
import { encodeKeys } from '../../internal/binary/EncodeKeys.js';

export function encodeBody(messageBody: Record<string, any>, binaryEncoder: BinaryEncoding): Map<any, any> {
    return encodeKeys(messageBody, binaryEncoder);
}
