//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { BinaryEncoding } from '../../internal/binary/BinaryEncoding.js';
import { decodeKeys } from '../../internal/binary/DecodeKeys.js';

export function decodeBody(encodedMessageBody: Map<any, any>, binaryEncoder: BinaryEncoding): Record<string, any> {
    return decodeKeys(encodedMessageBody, binaryEncoder);
}
