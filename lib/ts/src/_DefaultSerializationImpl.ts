import { decode, encode } from 'msgpackr';

export class _DefaultSerializationImpl {
    public toJson(uapiMessage: any): Uint8Array {
        const jsonStr = JSON.stringify(uapiMessage);
        return new TextEncoder().encode(jsonStr);
    }

    public toMsgPack(uapiMessage: any): Uint8Array {
        return encode(uapiMessage);
    }

    public fromJson(bytes: Uint8Array): any {
        const jsonStr = new TextDecoder().decode(bytes);
        return JSON.parse(jsonStr);
    }

    public fromMsgPack(bytes: Uint8Array): any {
        return decode(bytes);
    }
}
