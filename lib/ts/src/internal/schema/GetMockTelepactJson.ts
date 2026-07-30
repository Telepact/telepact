//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import mockInternalTelepact from '../../../inc/mock-internal.telepact.json';

export function getMockTelepactJson(): string {
    return JSON.stringify(mockInternalTelepact);
}
