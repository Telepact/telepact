import { bytesName } from '../../internal/types/TBytes';
import { ValidationFailure } from './ValidationFailure';
import { ValidateContext } from './ValidateContext';
import { getTypeUnexpectedValidationFailure } from './GetTypeUnexpectedValidationFailure';

export function validateBytes(value: unknown, ctx: ValidateContext): ValidationFailure[] {
    if (value instanceof Uint8Array) {
        console.log(`Value is of type 'Uint8Array':`, value);
        if (ctx.coerceBase64) {
            console.log(`Coercion to base64 is enabled. Context path: ${ctx.path}, Base64 Coercions:`, ctx.base64Coercions);
            setCoercedPath(ctx.path, ctx.base64Coercions);
        }
        return [];
    }
    if (typeof value === 'string') {
        console.log(`Value is of type 'string': ${value}. Attempting base64 decoding.`);
        try {
            const decoded = Buffer.from(value, 'base64').toString('binary'); // Decodes a base64-encoded string
            const reEncoded = Buffer.from(decoded, 'binary').toString('base64');
            if (reEncoded !== value) {
                throw Error('Invalid base64')
            }
            console.log(`Base64 decoding successful for value: ${value}`);
            if (!ctx.coerceBase64) {
                console.log(`Coercion to bytes is enabled. Context path: ${ctx.path}, Bytes Coercions:`, ctx.bytesCoercions);
                setCoercedPath(ctx.path, ctx.bytesCoercions);
            }
            return [];
        } catch (e) {
            console.log(`Base64 decoding failed for value: ${value}. Error:`, e);
            return getTypeUnexpectedValidationFailure([], value, 'Base64String');
        }
    } else {
        console.log(`Value is of unexpected type: ${typeof value}. Value:`, value);
        return getTypeUnexpectedValidationFailure([], value, bytesName);
    }
}

function setCoercedPath(path: string[], coercedPath: Record<string, unknown>): void {
    console.log(`Setting coerced path. Path: ${path}, Current coercedPath:`, coercedPath);
    const part = path[0];
    console.log(`Current part: ${part}`);

    if (path.length > 1) {
        console.log(`Path has more parts: ${path.slice(1)}. Updating coercedPath for part: ${part}`);
        coercedPath[part] = coercedPath[part] || {};
        setCoercedPath(path.slice(1), coercedPath[part] as Record<string, unknown>);
    } else {
        console.log(`Final part reached. Setting ${part} to true in coercedPath.`);
        coercedPath[part] = true;
    }
}