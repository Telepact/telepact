//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { Message } from '../Message.js';
import { TelepactError } from '../TelepactError.js';

export function buildUnknownErrorMessage(error: TelepactError, headers: Record<string, any> = {}): Message {
    return new Message(headers, { ErrorUnknown_: { caseId: error.caseId } });
}
