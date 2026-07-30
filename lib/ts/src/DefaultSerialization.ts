//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { Packr, Unpackr } from 'msgpackr';
import { Serialization } from './Serialization.js';

export class DefaultSerialization implements Serialization {
    private textEncoder = new TextEncoder();
    private textDecoder = new TextDecoder();
    private packr = new Packr({ mapsAsObjects: false, useRecords: false });
    private unpackr = new Unpackr({ mapsAsObjects: false, useRecords: false });

    public toJson(telepactMessage: any): Uint8Array {
        const jsonStr = JSON.stringify(telepactMessage);
        return this.textEncoder.encode(jsonStr);
    }

    public toMsgpack(telepactMessage: any): Uint8Array {
        return this.packr.encode(telepactMessage);
    }

    public fromJson(bytes: Uint8Array): any {
        const jsonStr = this.textDecoder.decode(bytes);
        return JSON.parse(jsonStr);
    }

    public fromMsgpack(bytes: Uint8Array): any {
        return this.unpackr.decode(bytes);
    }
}
