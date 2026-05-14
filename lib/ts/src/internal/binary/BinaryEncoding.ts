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

export class BinaryEncoding {
    public readonly encodeMap: Map<string, number>;
    public readonly decodeMap: Map<number, string>;
    public readonly checksum: number;
    public readonly keys: string[];
    public readonly requestPlanDescriptors: any[][];
    public readonly responsePlanDescriptors: any[][];

    constructor(
        binaryEncodingMap: Map<string, number>,
        checksum: number,
        keys?: string[],
        requestPlanDescriptors?: any[][],
        responsePlanDescriptors?: any[][],
    ) {
        this.encodeMap = binaryEncodingMap;
        const decodeList: [number, string][] = [...binaryEncodingMap.entries()].map((e: [string, number]) => [
            e[1],
            e[0],
        ]);
        this.decodeMap = new Map(decodeList);
        this.checksum = checksum;
        this.keys = keys ?? [...this.decodeMap.entries()].sort((a, b) => a[0] - b[0]).map((entry) => entry[1]);
        this.requestPlanDescriptors = requestPlanDescriptors ?? [];
        this.responsePlanDescriptors = responsePlanDescriptors ?? [];
    }

    negotiationDescriptor(functionId: number | undefined, includeBundle: boolean): Record<string, any> {
        const descriptor: Record<string, any> = { v: 1 };
        if (functionId !== undefined) {
            descriptor.p = functionId;
        }
        if (includeBundle) {
            descriptor.k = this.keys;
            descriptor.q = this.requestPlanDescriptors;
            descriptor.s = this.responsePlanDescriptors;
        }
        return descriptor;
    }

    static fromNegotiationDescriptor(checksum: number, descriptor: Record<string, any>): BinaryEncoding {
        const keys = (descriptor.k as string[]) ?? [];
        const encodingMap = new Map<string, number>();
        keys.forEach((key, index) => encodingMap.set(key, index));
        return new BinaryEncoding(
            encodingMap,
            checksum,
            keys,
            (descriptor.q as any[][] | undefined) ?? [],
            (descriptor.s as any[][] | undefined) ?? [],
        );
    }
}
