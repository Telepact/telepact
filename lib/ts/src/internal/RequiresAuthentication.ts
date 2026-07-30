//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { TelepactSchema } from '../TelepactSchema.js';

export function requiresAuthentication(telepactSchema: TelepactSchema, functionName: string): boolean {
    const functionDefinition = telepactSchema.full.find(
        (definition): definition is Record<string, unknown> =>
            typeof definition === 'object'
            && definition !== null
            && !Array.isArray(definition)
            && functionName in definition,
    );
    if (functionName.endsWith('_') || functionDefinition?.['$internal'] === true) {
        return false;
    }

    if (!('union.Auth_' in telepactSchema.parsed)) {
        return false;
    }

    return functionDefinition?.['$authenticated'] !== false;
}
