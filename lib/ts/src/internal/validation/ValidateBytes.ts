//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

import { bytesName } from '../../internal/types/TBytes';
import { ValidationFailure } from './ValidationFailure';
import { ValidateContext } from './ValidateContext';
import { getTypeUnexpectedValidationFailure } from './GetTypeUnexpectedValidationFailure';
import { decodeBase64, encodeBase64 } from '../binary/Base64Util';

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