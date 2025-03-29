import { decodeBase64 } from "./Base64Util";

export function clientBase64Decode(message: object[]): void {
    const headers = message[0] as Record<string, unknown>;
    const body = message[1] as Record<string, unknown>;

    const base64Paths = (headers["@base64_"] || {}) as Record<string, unknown>;

    travelBase64Decode(body, base64Paths);
}

function travelBase64Decode(value: unknown, base64Paths: unknown): unknown {
    if (typeof base64Paths === "object" && base64Paths !== null && !Array.isArray(base64Paths)) {
        for (const [key, val] of Object.entries(base64Paths)) {
            if (val === true) {
                if (key === "*" && Array.isArray(value)) {
                    for (let i = 0; i < value.length; i++) {
                        value[i] = travelBase64Decode(value[i], val);
                    }
                } else if (key === "*" && typeof value === "object" && value !== null) {
                    for (const k in value) {
                        if (Object.prototype.hasOwnProperty.call(value, k)) {
                            (value as Record<string, unknown>)[k] = travelBase64Decode((value as Record<string, unknown>)[k], val);
                        }
                    }
                } else if (typeof value === "object" && value !== null) {
                    (value as Record<string, unknown>)[key] = travelBase64Decode((value as Record<string, unknown>)[key], val);
                } else {
                    throw new Error(`Invalid base64 path: ${key} for value: ${value}`);
                }
            } else {
                if (key === "*" && Array.isArray(value)) {
                    for (const v of value) {
                        travelBase64Decode(v, val);
                    }
                } else if (key === "*" && typeof value === "object" && value !== null) {
                    for (const k in value) {
                        if (Object.prototype.hasOwnProperty.call(value, k)) {
                            travelBase64Decode((value as Record<string, unknown>)[k], val);
                        }
                    }
                } else if (typeof value === "object" && value !== null) {
                    travelBase64Decode((value as Record<string, unknown>)[key], val);
                } else {
                    throw new Error(`Invalid base64 path: ${key} for value: ${value}`);
                }
            }
        }
        return null;
    } else if (base64Paths === true && (typeof value === "string" || value === null)) {
        if (value === null) {
            return null;
        }
        const result = decodeBase64(value as string)
        return result;
    } else {
        throw new Error(`Invalid base64 path: ${base64Paths} for value: ${value}`);
    }
}