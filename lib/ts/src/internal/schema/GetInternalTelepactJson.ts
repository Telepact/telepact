//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import internalTelepact from '../../../inc/internal.telepact.json';

export function getInternalTelepactJson(): string {
    return JSON.stringify(internalTelepact);
}
