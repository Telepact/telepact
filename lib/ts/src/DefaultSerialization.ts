import { Packr, Unpackr } from 'msgpackr';
import { Serialization } from './Serialization';

export class DefaultSerialization implements Serialization {
    private packr = new Packr({ mapsAsObjects: false, useRecords: false });
    private unpackr = new Unpackr({ mapsAsObjects: false, useRecords: false });

    public toJson(uapiMessage: any): Uint8Array {
        const jsonStr = JSON.stringify(uapiMessage);
        return new TextEncoder().encode(jsonStr);
    }

    public toMsgpack(uapiMessage: any): Uint8Array {
        return this.packr.encode(uapiMessage);
    }

    public fromJson(bytes: Uint8Array): any {
        const jsonStr = new TextDecoder().decode(bytes);
        return JSON.parse(jsonStr);
    }

    public fromMsgpack(bytes: Uint8Array): any {
        return this.unpackr.decode(bytes);
    }
}
