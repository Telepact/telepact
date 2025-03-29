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

import { ExUnion, ExStruct, ServerHandler_, example, test, Value } from './gen/all_.js';

export class CodeGenHandler extends ServerHandler_ {

    async example(headers: { [key: string]: any }, input: example.Input): Promise<[ { [key: string]: any }, example.Output ]> {
        throw new Error("Unimplemented method 'example'");
    }

    async test(headers: { [key: string]: any }, input: test.Input): Promise<[Record<string, any>, test.Output]> {
        let value = new Value({});

        try {
            console.log("input: " + JSON.stringify(input.pseudoJson));
        } catch (e) {
            console.error(e);
        }

        const top = input.value();
        if (top) {
            if (top.bool() !== undefined) {
                value = Value.fromTyped({ bool: top.bool() });
            }
            if (top.nullBool() !== undefined) {
                value = Value.fromTyped({ nullBool: top.nullBool() });
            }
            if (top.arrBool() !== undefined) {
                value = Value.fromTyped({ arrBool: top.arrBool() });
            }
            if (top.arrNullBool() !== undefined) {
                value = Value.fromTyped({ arrNullBool: top.arrNullBool() });
            }
            if (top.objBool() !== undefined) {
                value = Value.fromTyped({ objBool: top.objBool() });
            }
            if (top.objNullBool() !== undefined) {
                value = Value.fromTyped({ objNullBool: top.objNullBool() });
            }
            if (top.int() !== undefined) {
                value = Value.fromTyped({ int: top.int() });
            }
            if (top.nullInt() !== undefined) {
                value = Value.fromTyped({ nullInt: top.nullInt() });
            }
            if (top.arrInt() !== undefined) {
                value = Value.fromTyped({ arrInt: top.arrInt() });
            }
            if (top.arrNullInt() !== undefined) {
                value = Value.fromTyped({ arrNullInt: top.arrNullInt() });
            }
            if (top.objInt() !== undefined) {
                value = Value.fromTyped({ objInt: top.objInt() });
            }
            if (top.objNullInt() !== undefined) {
                value = Value.fromTyped({ objNullInt: top.objNullInt() });
            }
            if (top.num() !== undefined) {
                value = Value.fromTyped({ num: top.num() });
            }
            if (top.nullNum() !== undefined) {
                value = Value.fromTyped({ nullNum: top.nullNum() });
            }
            if (top.arrNum() !== undefined) {
                value = Value.fromTyped({ arrNum: top.arrNum() });
            }
            if (top.arrNullNum() !== undefined) {
                value = Value.fromTyped({ arrNullNum: top.arrNullNum() });
            }
            if (top.objNum() !== undefined) {
                value = Value.fromTyped({ objNum: top.objNum() });
            }
            if (top.objNullNum() !== undefined) {
                value = Value.fromTyped({ objNullNum: top.objNullNum() });
            }
            if (top.str() !== undefined) {
                value = Value.fromTyped({ str: top.str() });
            }
            if (top.nullStr() !== undefined) {
                value = Value.fromTyped({ nullStr: top.nullStr() });
            }
            if (top.arrStr() !== undefined) {
                value = Value.fromTyped({ arrStr: top.arrStr() });
            }
            if (top.arrNullStr() !== undefined) {
                value = Value.fromTyped({ arrNullStr: top.arrNullStr() });
            }
            if (top.objStr() !== undefined) {
                value = Value.fromTyped({ objStr: top.objStr() });
            }
            if (top.objNullStr() !== undefined) {
                value = Value.fromTyped({ objNullStr: top.objNullStr() });
            }
            if (top.arr() !== undefined) {
                value = Value.fromTyped({ arr: top.arr() });
            }
            if (top.nullArr() !== undefined) {
                value = Value.fromTyped({ nullArr: top.nullArr() });
            }
            if (top.arrArr() !== undefined) {
                value = Value.fromTyped({ arrArr: top.arrArr() });
            }
            if (top.arrNullArr() !== undefined) {
                value = Value.fromTyped({ arrNullArr: top.arrNullArr() });
            }
            if (top.objArr() !== undefined) {
                value = Value.fromTyped({ objArr: top.objArr() });
            }
            if (top.objNullArr() !== undefined) {
                value = Value.fromTyped({ objNullArr: top.objNullArr() });
            }
            if (top.obj() !== undefined) {
                value = Value.fromTyped({ obj: top.obj() });
            }
            if (top.nullObj() !== undefined) {
                value = Value.fromTyped({ nullObj: top.nullObj() });
            }
            if (top.arrObj() !== undefined) {
                value = Value.fromTyped({ arrObj: top.arrObj() });
            }
            if (top.arrNullObj() !== undefined) {
                value = Value.fromTyped({ arrNullObj: top.arrNullObj() });
            }
            if (top.objObj() !== undefined) {
                value = Value.fromTyped({ objObj: top.objObj() });
            }
            if (top.objNullObj() !== undefined) {
                value = Value.fromTyped({ objNullObj: top.objNullObj() });
            }
            if (top.any() !== undefined) {
                value = Value.fromTyped({ any: top.any() });
            }
            if (top.nullAny() !== undefined) {
                value = Value.fromTyped({ nullAny: top.nullAny() });
            }
            if (top.arrAny() !== undefined) {
                value = Value.fromTyped({ arrAny: top.arrAny() });
            }
            if (top.arrNullAny() !== undefined) {
                value = Value.fromTyped({ arrNullAny: top.arrNullAny() });
            }
            if (top.objAny() !== undefined) {
                value = Value.fromTyped({ objAny: top.objAny() });
            }
            if (top.objNullAny() !== undefined) {
                value = Value.fromTyped({ objNullAny: top.objNullAny() });
            }
            if (top.bytes() !== undefined) {
                value = Value.fromTyped({ bytes: top.bytes() });
            }
            if (top.nullBytes() !== undefined) {
                value = Value.fromTyped({ nullBytes: top.nullBytes() });
            }
            if (top.arrBytes() !== undefined) {
                value = Value.fromTyped({ arrBytes: top.arrBytes() });
            }
            if (top.arrNullBytes() !== undefined) {
                value = Value.fromTyped({ arrNullBytes: top.arrNullBytes() });
            }
            if (top.objBytes() !== undefined) {
                value = Value.fromTyped({ objBytes: top.objBytes() });
            }
            if (top.objNullBytes() !== undefined) {
                value = Value.fromTyped({ objNullBytes: top.objNullBytes() });
            }            
            if (top.struct() !== undefined) {
                value = Value.fromTyped({ struct: mapStruct(top.struct()!) });
            }
            if (top.nullStruct() !== undefined) {
                value = Value.fromTyped({ nullStruct: top.nullStruct() === null ? null : mapStruct(top.nullStruct()!) });
            }
            if (top.arrStruct() !== undefined) {
                value = Value.fromTyped({ arrStruct: map_arr(top.arrStruct()!, mapStruct) });
            }
            if (top.arrNullStruct() !== undefined) {
                value = Value.fromTyped({ arrNullStruct: map_arr(top.arrNullStruct()!, (e) => e === null ? null : mapStruct(e)) });
            }
            if (top.objStruct() !== undefined) {
                value = Value.fromTyped({ objStruct: map_obj(top.objStruct()!, mapStruct) });
            }
            if (top.objNullStruct() !== undefined) {
                value = Value.fromTyped({ objNullStruct: map_obj(top.objNullStruct()!, (e) => e === null ? null : mapStruct(e)) });
            }
            if (top.union() !== undefined) {
                value = Value.fromTyped({ union: map_union(top.union()!) });
            }
            if (top.nullUnion() !== undefined) {
                value = Value.fromTyped({ nullUnion: top.nullUnion() === null ? null : map_union(top.nullUnion()!) });
            }
            if (top.arrUnion() !== undefined) {
                value = Value.fromTyped({ arrUnion: map_arr(top.arrUnion()!, map_union) });
            }
            if (top.arrNullUnion() !== undefined) {
                value = Value.fromTyped({ arrNullUnion: map_arr(top.arrNullUnion()!, (e) => e === null ? null : map_union(e)) });
            }
            if (top.objUnion() !== undefined) {
                value = Value.fromTyped({ objUnion: map_obj(top.objUnion()!, map_union) });
            }
            if (top.objNullUnion() !== undefined) {
                value = Value.fromTyped({ objNullUnion: map_obj(top.objNullUnion()!, (e) => e === null ? null : map_union(e)) });
            }
            if (top.fn() !== undefined) {
                value = Value.fromTyped({ fn: map_fn(top.fn()!) });
            }
            if (top.nullFn() !== undefined) {
                value = Value.fromTyped({ nullFn: top.nullFn() === null ? null : map_fn(top.nullFn()!) });
            }
            if (top.arrFn() !== undefined) {
                value = Value.fromTyped({ arrFn: map_arr(top.arrFn()!, map_fn) });
            }
            if (top.arrNullFn() !== undefined) {
                value = Value.fromTyped({ arrNullFn: map_arr(top.arrNullFn()!, (e) => e === null ? null : map_fn(e)) });
            }
            if (top.objFn() !== undefined) {
                value = Value.fromTyped({ objFn: map_obj(top.objFn()!, map_fn) });
            }
            if (top.objNullFn() !== undefined) {
                value = Value.fromTyped({ objNullFn: map_obj(top.objNullFn()!, (e) => e === null ? null : map_fn(e)) });
            }
        }

        let output = test.Output.from_Ok_(test.Output.Ok_.fromTyped({ value }));

        return [{}, output];
    }
}


function mapStruct(s: ExStruct): ExStruct {
    const args: { required: boolean, optional?: boolean, optional2?: number} = {
        required: s.required()
    }
    if (s.optional() !== undefined) {
        args.optional = s.optional();
    }
    if (s.optional2() !== undefined) {
        args.optional2 = s.optional2();
    }
    return ExStruct.fromTyped(args);
} 

function map_union(u: ExUnion): ExUnion {
    var tv = u.getTaggedValue();
    if (tv.tag === 'One') {
        return ExUnion.from_One(ExUnion.One.fromTyped({}));
    } else if (tv.tag === 'Two') {
        const args: { required: boolean, optional?: boolean} = {
            required: tv.value.required()
        }
        if (tv.value.optional() !== undefined) {
            args.optional = tv.value.optional();
        }
        return ExUnion.from_Two(ExUnion.Two.fromTyped(args));
    } else {
        throw new Error("Unknown union type: " + u.constructor.name);
    }
}

function map_fn(f: example.Input): example.Input {
    const args: { required: boolean, optional?: boolean} = {
        required: f.required()
    }
    if (f.optional() !== undefined) {
        args.optional = f.optional();
    }
    return example.Input.fromTyped(args);
}

function map_arr<T>(l: T[], mapper: (item: T) => T): T[] {
    return l.map(mapper);
}

function map_obj<T>(m: { [key: string]: T }, mapper: (item: T) => T): { [key: string]: T } {
    const result: { [key: string]: T } = {};
    for (const key in m) {
        if (m.hasOwnProperty(key)) {
            result[key] = mapper(m[key]!);
        }
    }
    return result;
}