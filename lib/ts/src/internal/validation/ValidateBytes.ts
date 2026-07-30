//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { bytesName } from '../../internal/types/TBytes.js';
import { ValidationFailure } from './ValidationFailure.js';
import { ValidateContext } from './ValidateContext.js';
import { getTypeUnexpectedValidationFailure } from './GetTypeUnexpectedValidationFailure.js';
import { decodeBase64, encodeBase64 } from '../binary/Base64Util.js';

export function validateBytes(value: unknown, ctx: ValidateContext): ValidationFailure[] {
    if (value instanceof Uint8Array) {
        if (ctx.coerceBase64) {
            setCoercedPath(ctx.path, ctx.base64Coercions);
        }
        return [];
    }
    if (typeof value === 'string') {
        try {
            const decoded = decodeBase64(value);
            const reEncoded = encodeBase64(decoded);
            if (reEncoded !== value) {
                throw Error('Invalid base64')
            }
            if (!ctx.coerceBase64) {
                setCoercedPath(ctx.path, ctx.bytesCoercions);
            }
            return [];
        } catch (e) {
            return getTypeUnexpectedValidationFailure([], value, 'Base64String');
        }
    } else {
        return getTypeUnexpectedValidationFailure([], value, bytesName);
    }
}

function setCoercedPath(path: string[], coercedPath: Record<string, unknown>): void {
    const part = path[0];

    if (path.length > 1) {
        coercedPath[part] = coercedPath[part] || {};
        setCoercedPath(path.slice(1), coercedPath[part] as Record<string, unknown>);
    } else {
        coercedPath[part] = true;
    }
}