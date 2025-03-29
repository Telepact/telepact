export function clientBase64Encode(message: Array<any>): void {
    const body = message[1] as Record<string, any>;

    travelBase64Encode(body);
}

function travelBase64Encode(value: any): void {
    if (typeof value === "object" && !Array.isArray(value)) {
        for (const [key, val] of Object.entries(value)) {
            if (val instanceof Uint8Array) {
                value[key] = btoa(String.fromCharCode(...val));
            } else {
                travelBase64Encode(val);
            }
        }
    } else if (Array.isArray(value)) {
        for (let i = 0; i < value.length; i++) {
            const v = value[i];
            if (v instanceof Uint8Array) {
                value[i] = btoa(String.fromCharCode(...v));
            } else {
                travelBase64Encode(v);
            }
        }
    }
}