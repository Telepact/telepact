import { Buffer } from "buffer";

export function serverBase64Decode(body: Record<string, any>, bytesPaths: Record<string, any>): void {
    travelBase64Decode(body, bytesPaths);
}

function travelBase64Decode(value: any, bytesPaths: any): any {
    if (typeof bytesPaths === "object" && !Array.isArray(bytesPaths)) {
        for (const [key, val] of Object.entries(bytesPaths)) {
            if (val === true) {
                if (key === "*" && Array.isArray(value)) {
                    for (let i = 0; i < value.length; i++) {
                        const nv = travelBase64Decode(value[i], val);
                        value[i] = nv;
                    }
                } else if (key === "*" && typeof value === "object" && value !== null) {
                    for (const [k, v] of Object.entries(value)) {
                        const nv = travelBase64Decode(v, val);
                        value[k] = nv;
                    }
                } else if (typeof value === "object" && value !== null) {
                    const nv = travelBase64Decode(value[key], val);
                    value[key] = nv;
                } else {
                    throw new Error(`Invalid bytes path: ${key} for value: ${value}`);
                }
            } else {
                if (key === "*" && Array.isArray(value)) {
                    for (let i = 0; i < value.length; i++) {
                        travelBase64Decode(value[i], val);
                    }
                } else if (key === "*" && typeof value === "object" && value !== null) {
                    for (const [k, v] of Object.entries(value)) {
                        travelBase64Decode(v, val);
                    }
                } else if (typeof value === "object" && value !== null) {
                    travelBase64Decode(value[key], val);
                } else {
                    throw new Error(`Invalid bytes path: ${key} for value: ${value}`);
                }
            }
        }
        return null;
    } else if (bytesPaths === true && (typeof value === "string" || value === null)) {
        if (value === null) {
            return null;
        }
        const decodedValue = Buffer.from(value, "base64");
        return decodedValue;
    } else {
        throw new Error(`Invalid bytes path: ${bytesPaths} for value: ${value} of type ${typeof value}`);
    }
}