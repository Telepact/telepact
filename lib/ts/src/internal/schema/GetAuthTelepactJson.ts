//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import authTelepact from '../../../inc/auth.telepact.json';

export function getAuthTelepactJson(): string {
    return JSON.stringify(authTelepact);
}
