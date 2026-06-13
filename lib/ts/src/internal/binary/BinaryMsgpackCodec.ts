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

import { BinaryEncoding } from './BinaryEncoding.js';
import { BinaryEncodingMissing } from './BinaryEncodingMissing.js';
import type { MsgpackHeaders } from './BinaryMsgpackSerialization.js';

export class BinaryMsgpackCodec {
    private readonly textEncoder = new TextEncoder();
    private readonly textDecoder = new TextDecoder();
    private readonly encodedStrings = new Map<string, Uint8Array>();

    public toBinaryMsgpack(headers: Record<string, any>, body: Record<string, any>, binaryEncoding: BinaryEncoding): Uint8Array {
        const writer = new MsgpackWriter(this.textEncoder, this.encodedStrings);
        writer.packArrayHeader(2);
        writer.packValue(headers, undefined, false);
        writer.packValue(body, binaryEncoding, true);
        return writer.toBytes();
    }

    public fromMsgpackHeaders(bytes: Uint8Array): MsgpackHeaders {
        const reader = new MsgpackReader(bytes, this.textDecoder);
        const length = reader.unpackArrayHeader();
        if (length !== 2) {
            throw new Error('expected Telepact msgpack message array');
        }
        const headers = reader.unpackValue(undefined, false) as Record<string, any>;
        return { headers, bodyOffset: reader.offset };
    }

    public fromMsgpackBody(bytes: Uint8Array, offset: number, binaryEncoding: BinaryEncoding): Record<string, any> {
        const reader = new MsgpackReader(bytes, this.textDecoder, offset);
        return reader.unpackValue(binaryEncoding, true) as Record<string, any>;
    }
}

class MsgpackWriter {
    private buffer = new Uint8Array(65536);
    private view = new DataView(this.buffer.buffer);
    private offset = 0;

    constructor(
        private readonly textEncoder: TextEncoder,
        private readonly encodedStrings: Map<string, Uint8Array>,
    ) {}

    public toBytes(): Uint8Array {
        return this.buffer.subarray(0, this.offset);
    }

    public packArrayHeader(length: number): void {
        if (length < 16) {
            this.writeByte(0x90 | length);
        } else if (length <= 0xffff) {
            this.writeByte(0xdc);
            this.writeUint16(length);
        } else {
            this.writeByte(0xdd);
            this.writeUint32(length);
        }
    }

    public packValue(value: any, binaryEncoding: BinaryEncoding | undefined, translateKeys: boolean): void {
        if (value === null || value === undefined) {
            this.writeByte(0xc0);
            return;
        }

        if (typeof value === 'string') {
            this.packString(value);
            return;
        }

        if (typeof value === 'boolean') {
            this.writeByte(value ? 0xc3 : 0xc2);
            return;
        }

        if (typeof value === 'number') {
            this.packNumber(value);
            return;
        }

        if (Array.isArray(value)) {
            if (translateKeys && binaryEncoding !== undefined && this.tryPackUniformObjectArray(value, binaryEncoding)) {
                return;
            }
            this.packArrayHeader(value.length);
            for (let index = 0; index < value.length; index += 1) {
                this.packValue(value[index], binaryEncoding, translateKeys);
            }
            return;
        }

        if (value instanceof Uint8Array) {
            this.packBinary(value);
            return;
        }

        if (value instanceof ArrayBuffer) {
            this.packBinary(new Uint8Array(value));
            return;
        }

        if (ArrayBuffer.isView(value)) {
            this.packBinary(new Uint8Array(value.buffer, value.byteOffset, value.byteLength));
            return;
        }

        if (value instanceof Map) {
            this.packMapHeader(value.size);
            for (const [key, entryValue] of value.entries()) {
                this.packMapKey(key, binaryEncoding, translateKeys);
                this.packValue(entryValue, binaryEncoding, translateKeys);
            }
            return;
        }

        if (typeof value === 'object') {
            const keys = Object.keys(value);
            this.packMapHeader(keys.length);
            for (let index = 0; index < keys.length; index += 1) {
                const key = keys[index]!;
                this.packMapKey(key, binaryEncoding, translateKeys);
                this.packValue(value[key], binaryEncoding, translateKeys);
            }
            return;
        }

        throw new Error(`unsupported msgpack value type: ${typeof value}`);
    }

    private tryPackUniformObjectArray(value: any[], binaryEncoding: BinaryEncoding): boolean {
        if (value.length < 16) {
            return false;
        }

        const first = value[0];
        if (first === null || typeof first !== 'object' || Array.isArray(first) || first instanceof Map || ArrayBuffer.isView(first)) {
            return false;
        }

        const keys = Object.keys(first);
        if (keys.length === 0) {
            return false;
        }

        const encodedKeys = new Array<number>(keys.length);
        for (let index = 0; index < keys.length; index += 1) {
            const encoded = binaryEncoding.encodeMap.get(keys[index]!);
            if (encoded === undefined) {
                return false;
            }
            encodedKeys[index] = encoded;
        }

        this.packArrayHeader(value.length);
        for (let itemIndex = 0; itemIndex < value.length; itemIndex += 1) {
            const item = value[itemIndex]!;
            this.packMapHeader(keys.length);
            for (let keyIndex = 0; keyIndex < keys.length; keyIndex += 1) {
                this.packNumber(encodedKeys[keyIndex]!);
                this.packValue(item[keys[keyIndex]!], binaryEncoding, true);
            }
        }
        return true;
    }

    private packMapKey(key: any, binaryEncoding: BinaryEncoding | undefined, translateKeys: boolean): void {
        if (translateKeys && typeof key === 'string' && binaryEncoding !== undefined) {
            const encoded = binaryEncoding.encodeMap.get(key);
            if (encoded !== undefined) {
                this.packNumber(encoded);
                return;
            }
        }
        this.packValue(key, undefined, false);
    }

    private packMapHeader(length: number): void {
        if (length < 16) {
            this.writeByte(0x80 | length);
        } else if (length <= 0xffff) {
            this.writeByte(0xde);
            this.writeUint16(length);
        } else {
            this.writeByte(0xdf);
            this.writeUint32(length);
        }
    }

    private packString(value: string): void {
        let packed = this.encodedStrings.get(value);
        if (packed !== undefined) {
            this.writeBytes(packed);
            return;
        }

        if (this.packAsciiString(value)) {
            return;
        }

        const bytes = this.textEncoder.encode(value);
        const length = bytes.length;
        let headerLength: number;
        if (length < 32) {
            headerLength = 1;
        } else if (length <= 0xff) {
            headerLength = 2;
        } else if (length <= 0xffff) {
            headerLength = 3;
        } else {
            headerLength = 5;
        }
        packed = new Uint8Array(headerLength + length);
        const view = new DataView(packed.buffer);
        if (length < 32) {
            packed[0] = 0xa0 | length;
        } else if (length <= 0xff) {
            packed[0] = 0xd9;
            packed[1] = length;
        } else if (length <= 0xffff) {
            packed[0] = 0xda;
            view.setUint16(1, length);
        } else {
            packed[0] = 0xdb;
            view.setUint32(1, length);
        }
        packed.set(bytes, headerLength);
        this.encodedStrings.set(value, packed);
        this.writeBytes(packed);
    }

    private packAsciiString(value: string): boolean {
        const length = value.length;
        let headerLength: number;
        if (length < 32) {
            headerLength = 1;
        } else if (length <= 0xff) {
            headerLength = 2;
        } else if (length <= 0xffff) {
            headerLength = 3;
        } else {
            headerLength = 5;
        }

        this.ensure(headerLength + length);
        const stringOffset = this.offset + headerLength;
        for (let index = 0; index < length; index += 1) {
            const code = value.charCodeAt(index);
            if (code > 0x7f) {
                return false;
            }
            this.buffer[stringOffset + index] = code;
        }

        if (length < 32) {
            this.buffer[this.offset] = 0xa0 | length;
        } else if (length <= 0xff) {
            this.buffer[this.offset] = 0xd9;
            this.buffer[this.offset + 1] = length;
        } else if (length <= 0xffff) {
            this.buffer[this.offset] = 0xda;
            this.view.setUint16(this.offset + 1, length);
        } else {
            this.buffer[this.offset] = 0xdb;
            this.view.setUint32(this.offset + 1, length);
        }
        this.offset += headerLength + length;
        return true;
    }

    private packStringHeader(length: number): void {
        if (length < 32) {
            this.writeByte(0xa0 | length);
        } else if (length <= 0xff) {
            this.writeByte(0xd9);
            this.writeByte(length);
        } else if (length <= 0xffff) {
            this.writeByte(0xda);
            this.writeUint16(length);
        } else {
            this.writeByte(0xdb);
            this.writeUint32(length);
        }
    }

    private packBinary(bytes: Uint8Array): void {
        const length = bytes.length;
        if (length < 32) {
            this.writeByte(0xc4);
            this.writeByte(length);
        } else if (length <= 0xff) {
            this.writeByte(0xc4);
            this.writeByte(length);
        } else if (length <= 0xffff) {
            this.writeByte(0xc5);
            this.writeUint16(length);
        } else {
            this.writeByte(0xc6);
            this.writeUint32(length);
        }
        this.writeBytes(bytes);
    }

    private packNumber(value: number): void {
        if (!Number.isInteger(value) || !Number.isSafeInteger(value)) {
            this.writeByte(0xcb);
            this.writeFloat64(value);
            return;
        }

        if (value >= 0) {
            if (value <= 0x7f) {
                this.writeByte(value);
            } else if (value <= 0xff) {
                this.writeByte(0xcc);
                this.writeByte(value);
            } else if (value <= 0xffff) {
                this.writeByte(0xcd);
                this.writeUint16(value);
            } else if (value <= 0xffffffff) {
                this.writeByte(0xce);
                this.writeUint32(value);
            } else {
                this.writeByte(0xcf);
                this.writeBigUint64(BigInt(value));
            }
            return;
        }

        if (value >= -32) {
            this.writeByte(0x100 + value);
        } else if (value >= -0x80) {
            this.writeByte(0xd0);
            this.writeInt8(value);
        } else if (value >= -0x8000) {
            this.writeByte(0xd1);
            this.writeInt16(value);
        } else if (value >= -0x80000000) {
            this.writeByte(0xd2);
            this.writeInt32(value);
        } else {
            this.writeByte(0xd3);
            this.writeBigInt64(BigInt(value));
        }
    }

    private ensure(bytes: number): void {
        const needed = this.offset + bytes;
        if (needed <= this.buffer.length) {
            return;
        }

        let nextLength = this.buffer.length * 2;
        while (nextLength < needed) {
            nextLength *= 2;
        }
        const next = new Uint8Array(nextLength);
        next.set(this.buffer);
        this.buffer = next;
        this.view = new DataView(this.buffer.buffer);
    }

    private writeByte(value: number): void {
        this.ensure(1);
        this.buffer[this.offset] = value & 0xff;
        this.offset += 1;
    }

    private writeBytes(bytes: Uint8Array): void {
        this.ensure(bytes.length);
        this.buffer.set(bytes, this.offset);
        this.offset += bytes.length;
    }

    private writeUint16(value: number): void {
        this.ensure(2);
        this.view.setUint16(this.offset, value);
        this.offset += 2;
    }

    private writeUint32(value: number): void {
        this.ensure(4);
        this.view.setUint32(this.offset, value);
        this.offset += 4;
    }

    private writeInt8(value: number): void {
        this.ensure(1);
        this.view.setInt8(this.offset, value);
        this.offset += 1;
    }

    private writeInt16(value: number): void {
        this.ensure(2);
        this.view.setInt16(this.offset, value);
        this.offset += 2;
    }

    private writeInt32(value: number): void {
        this.ensure(4);
        this.view.setInt32(this.offset, value);
        this.offset += 4;
    }

    private writeBigUint64(value: bigint): void {
        this.ensure(8);
        this.view.setBigUint64(this.offset, value);
        this.offset += 8;
    }

    private writeBigInt64(value: bigint): void {
        this.ensure(8);
        this.view.setBigInt64(this.offset, value);
        this.offset += 8;
    }

    private writeFloat64(value: number): void {
        this.ensure(8);
        this.view.setFloat64(this.offset, value);
        this.offset += 8;
    }
}

class MsgpackReader {
    public offset: number;

    private readonly view: DataView;

    constructor(private readonly bytes: Uint8Array, private readonly textDecoder: TextDecoder, offset = 0) {
        this.offset = offset;
        this.view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
    }

    public unpackArrayHeader(): number {
        const token = this.readByte();
        if (token >= 0x90 && token <= 0x9f) {
            return token & 0x0f;
        }
        if (token === 0xdc) {
            return this.readUint16();
        }
        if (token === 0xdd) {
            return this.readUint32();
        }
        throw new Error('expected msgpack array');
    }

    public unpackValue(binaryEncoding: BinaryEncoding | undefined, decodeKeys: boolean): any {
        const token = this.readByte();

        if (token <= 0x7f) {
            return token;
        }
        if (token >= 0xe0) {
            return token - 0x100;
        }
        if (token >= 0xa0 && token <= 0xbf) {
            return this.readString(token & 0x1f);
        }
        if (token >= 0x90 && token <= 0x9f) {
            return this.readArray(token & 0x0f, binaryEncoding, decodeKeys);
        }
        if (token >= 0x80 && token <= 0x8f) {
            return this.readMap(token & 0x0f, binaryEncoding, decodeKeys);
        }

        switch (token) {
            case 0xc0:
                return null;
            case 0xc2:
                return false;
            case 0xc3:
                return true;
            case 0xc4:
                return this.readBinary(this.readByte());
            case 0xc5:
                return this.readBinary(this.readUint16());
            case 0xc6:
                return this.readBinary(this.readUint32());
            case 0xca:
                return this.readFloat32();
            case 0xcb:
                return this.readFloat64();
            case 0xcc:
                return this.readByte();
            case 0xcd:
                return this.readUint16();
            case 0xce:
                return this.readUint32();
            case 0xcf:
                return Number(this.readBigUint64());
            case 0xd0:
                return this.readInt8();
            case 0xd1:
                return this.readInt16();
            case 0xd2:
                return this.readInt32();
            case 0xd3:
                return Number(this.readBigInt64());
            case 0xd9:
                return this.readString(this.readByte());
            case 0xda:
                return this.readString(this.readUint16());
            case 0xdb:
                return this.readString(this.readUint32());
            case 0xdc:
                return this.readArray(this.readUint16(), binaryEncoding, decodeKeys);
            case 0xdd:
                return this.readArray(this.readUint32(), binaryEncoding, decodeKeys);
            case 0xde:
                return this.readMap(this.readUint16(), binaryEncoding, decodeKeys);
            case 0xdf:
                return this.readMap(this.readUint32(), binaryEncoding, decodeKeys);
            default:
                throw new Error(`unsupported msgpack token: ${token}`);
        }
    }

    private readArray(length: number, binaryEncoding: BinaryEncoding | undefined, decodeKeys: boolean): any[] {
        const result = new Array(length);
        for (let index = 0; index < length; index += 1) {
            result[index] = this.unpackValue(binaryEncoding, decodeKeys);
        }
        return result;
    }

    private readMap(length: number, binaryEncoding: BinaryEncoding | undefined, decodeKeys: boolean): Record<string, any> {
        const result: Record<string, any> = {};
        for (let index = 0; index < length; index += 1) {
            const rawKey = this.unpackValue(undefined, false);
            const value = this.unpackValue(binaryEncoding, decodeKeys);
            const finalKey = decodeKeys ? this.decodeBinaryKey(rawKey, binaryEncoding) : String(rawKey);
            result[finalKey] = value;
        }
        return result;
    }

    private decodeBinaryKey(key: any, binaryEncoding: BinaryEncoding | undefined): string {
        if (typeof key === 'string') {
            return key;
        }
        if (typeof key === 'number' && Number.isInteger(key) && binaryEncoding !== undefined) {
            const decoded = binaryEncoding.decodeTable[key];
            if (decoded !== undefined) {
                return decoded;
            }
        }
        throw new BinaryEncodingMissing(key);
    }

    private readByte(): number {
        if (this.offset >= this.bytes.length) {
            throw new Error('unexpected end of msgpack payload');
        }
        const value = this.bytes[this.offset]!;
        this.offset += 1;
        return value;
    }

    private readString(length: number): string {
        this.ensure(length);
        const end = this.offset + length;
        const value = this.textDecoder.decode(this.bytes.subarray(this.offset, end));
        this.offset += length;
        return value;
    }

    private readBinary(length: number): Uint8Array {
        this.ensure(length);
        const value = this.bytes.slice(this.offset, this.offset + length);
        this.offset += length;
        return value;
    }

    private ensure(length: number): void {
        if (this.offset + length > this.bytes.length) {
            throw new Error('unexpected end of msgpack payload');
        }
    }

    private readUint16(): number {
        this.ensure(2);
        const value = this.view.getUint16(this.offset);
        this.offset += 2;
        return value;
    }

    private readUint32(): number {
        this.ensure(4);
        const value = this.view.getUint32(this.offset);
        this.offset += 4;
        return value;
    }

    private readInt8(): number {
        this.ensure(1);
        const value = this.view.getInt8(this.offset);
        this.offset += 1;
        return value;
    }

    private readInt16(): number {
        this.ensure(2);
        const value = this.view.getInt16(this.offset);
        this.offset += 2;
        return value;
    }

    private readInt32(): number {
        this.ensure(4);
        const value = this.view.getInt32(this.offset);
        this.offset += 4;
        return value;
    }

    private readBigUint64(): bigint {
        this.ensure(8);
        const value = this.view.getBigUint64(this.offset);
        this.offset += 8;
        return value;
    }

    private readBigInt64(): bigint {
        this.ensure(8);
        const value = this.view.getBigInt64(this.offset);
        this.offset += 8;
        return value;
    }

    private readFloat32(): number {
        this.ensure(4);
        const value = this.view.getFloat32(this.offset);
        this.offset += 4;
        return value;
    }

    private readFloat64(): number {
        this.ensure(8);
        const value = this.view.getFloat64(this.offset);
        this.offset += 8;
        return value;
    }
}
