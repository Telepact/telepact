import { encode, decode } from '@msgpack/msgpack';

export class _DefaultSerializer implements SerializationImpl {
    async toJson(uapiMessage: any): Promise<Buffer> {
        const jsonString = JSON.stringify(uapiMessage);
        return Buffer.from(jsonString);
    }

    async fromJson(bytes: Buffer): Promise<any> {
        const jsonString = bytes.toString('utf-8');
        return JSON.parse(jsonString);
    }

    async toMsgPack(uapiMessage: any): Promise<Buffer> {
        return Buffer.from(encode(uapiMessage));
    }

    async fromMsgPack(bytes: Buffer): Promise<any> {
        return decode(bytes);
    }
}