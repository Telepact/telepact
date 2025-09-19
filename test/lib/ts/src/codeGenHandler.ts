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

import { ExUnion, ExStruct, ServerHandler_, example, test, Value } from './gen/genTypes.js';

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
                value = Value.from({ bool: top.bool() });
            }
            if (top.nullBool() !== undefined) {
                value = Value.from({ nullBool: top.nullBool() });
            }
            if (top.arrBool() !== undefined) {
                value = Value.from({ arrBool: top.arrBool() });
            }
            if (top.arrNullBool() !== undefined) {
                value = Value.from({ arrNullBool: top.arrNullBool() });
            }
            if (top.objBool() !== undefined) {
                value = Value.from({ objBool: top.objBool() });
            }
            if (top.objNullBool() !== undefined) {
                value = Value.from({ objNullBool: top.objNullBool() });
            }
            if (top.int() !== undefined) {
                value = Value.from({ int: top.int() });
            }
            if (top.nullInt() !== undefined) {
                value = Value.from({ nullInt: top.nullInt() });
            }
            if (top.arrInt() !== undefined) {
                value = Value.from({ arrInt: top.arrInt() });
            }
            if (top.arrNullInt() !== undefined) {
                value = Value.from({ arrNullInt: top.arrNullInt() });
            }
            if (top.objInt() !== undefined) {
                value = Value.from({ objInt: top.objInt() });
            }
            if (top.objNullInt() !== undefined) {
                value = Value.from({ objNullInt: top.objNullInt() });
            }
            if (top.num() !== undefined) {
                value = Value.from({ num: top.num() });
            }
            if (top.nullNum() !== undefined) {
                value = Value.from({ nullNum: top.nullNum() });
            }
            if (top.arrNum() !== undefined) {
                value = Value.from({ arrNum: top.arrNum() });
            }
            if (top.arrNullNum() !== undefined) {
                value = Value.from({ arrNullNum: top.arrNullNum() });
            }
            if (top.objNum() !== undefined) {
                value = Value.from({ objNum: top.objNum() });
            }
            if (top.objNullNum() !== undefined) {
                value = Value.from({ objNullNum: top.objNullNum() });
            }
            if (top.str() !== undefined) {
                value = Value.from({ str: top.str() });
            }
            if (top.nullStr() !== undefined) {
                value = Value.from({ nullStr: top.nullStr() });
            }
            if (top.arrStr() !== undefined) {
                value = Value.from({ arrStr: top.arrStr() });
            }
            if (top.arrNullStr() !== undefined) {
                value = Value.from({ arrNullStr: top.arrNullStr() });
            }
            if (top.objStr() !== undefined) {
                value = Value.from({ objStr: top.objStr() });
            }
            if (top.objNullStr() !== undefined) {
                value = Value.from({ objNullStr: top.objNullStr() });
            }
            if (top.arr() !== undefined) {
                value = Value.from({ arr: top.arr() });
            }
            // if (top.nullArr() !== undefined) {
            //     value = Value.from({ nullArr: top.nullArr() });
            // }
            if (top.arrArr() !== undefined) {
                value = Value.from({ arrArr: top.arrArr() });
            }
            // if (top.arrNullArr() !== undefined) {
            //     value = Value.from({ arrNullArr: top.arrNullArr() });
            // }
            if (top.objArr() !== undefined) {
                value = Value.from({ objArr: top.objArr() });
            }
            // if (top.objNullArr() !== undefined) {
            //     value = Value.from({ objNullArr: top.objNullArr() });
            // }
            if (top.obj() !== undefined) {
                value = Value.from({ obj: top.obj() });
            }
            // if (top.nullObj() !== undefined) {
            //     value = Value.from({ nullObj: top.nullObj() });
            // }
            if (top.arrObj() !== undefined) {
                value = Value.from({ arrObj: top.arrObj() });
            }
            // if (top.arrNullObj() !== undefined) {
            //     value = Value.from({ arrNullObj: top.arrNullObj() });
            // }
            if (top.objObj() !== undefined) {
                value = Value.from({ objObj: top.objObj() });
            }
            // if (top.objNullObj() !== undefined) {
            //     value = Value.from({ objNullObj: top.objNullObj() });
            // }
            if (top.any() !== undefined) {
                value = Value.from({ any: top.any() });
            }
            if (top.nullAny() !== undefined) {
                value = Value.from({ nullAny: top.nullAny() });
            }
            if (top.arrAny() !== undefined) {
                value = Value.from({ arrAny: top.arrAny() });
            }
            if (top.arrNullAny() !== undefined) {
                value = Value.from({ arrNullAny: top.arrNullAny() });
            }
            if (top.objAny() !== undefined) {
                value = Value.from({ objAny: top.objAny() });
            }
            if (top.objNullAny() !== undefined) {
                value = Value.from({ objNullAny: top.objNullAny() });
            }
            if (top.bytes() !== undefined) {
                value = Value.from({ bytes: top.bytes() });
            }
            if (top.nullBytes() !== undefined) {
                value = Value.from({ nullBytes: top.nullBytes() });
            }
            if (top.arrBytes() !== undefined) {
                value = Value.from({ arrBytes: top.arrBytes() });
            }
            if (top.arrNullBytes() !== undefined) {
                value = Value.from({ arrNullBytes: top.arrNullBytes() });
            }
            if (top.objBytes() !== undefined) {
                value = Value.from({ objBytes: top.objBytes() });
            }
            if (top.objNullBytes() !== undefined) {
                value = Value.from({ objNullBytes: top.objNullBytes() });
            }            
            if (top.struct() !== undefined) {
                value = Value.from({ struct: mapStruct(top.struct()!) });
            }
            if (top.nullStruct() !== undefined) {
                value = Value.from({ nullStruct: top.nullStruct() === null ? null : mapStruct(top.nullStruct()!) });
            }
            if (top.arrStruct() !== undefined) {
                value = Value.from({ arrStruct: map_arr(top.arrStruct()!, mapStruct) });
            }
            if (top.arrNullStruct() !== undefined) {
                value = Value.from({ arrNullStruct: map_arr(top.arrNullStruct()!, (e) => e === null ? null : mapStruct(e)) });
            }
            if (top.objStruct() !== undefined) {
                value = Value.from({ objStruct: map_obj(top.objStruct()!, mapStruct) });
            }
            if (top.objNullStruct() !== undefined) {
                value = Value.from({ objNullStruct: map_obj(top.objNullStruct()!, (e) => e === null ? null : mapStruct(e)) });
            }
            if (top.union() !== undefined) {
                value = Value.from({ union: map_union(top.union()!) });
            }
            if (top.nullUnion() !== undefined) {
                value = Value.from({ nullUnion: top.nullUnion() === null ? null : map_union(top.nullUnion()!) });
            }
            if (top.arrUnion() !== undefined) {
                value = Value.from({ arrUnion: map_arr(top.arrUnion()!, map_union) });
            }
            if (top.arrNullUnion() !== undefined) {
                value = Value.from({ arrNullUnion: map_arr(top.arrNullUnion()!, (e) => e === null ? null : map_union(e)) });
            }
            if (top.objUnion() !== undefined) {
                value = Value.from({ objUnion: map_obj(top.objUnion()!, map_union) });
            }
            if (top.objNullUnion() !== undefined) {
                value = Value.from({ objNullUnion: map_obj(top.objNullUnion()!, (e) => e === null ? null : map_union(e)) });
            }
            if (top.fn() !== undefined) {
                value = Value.from({ fn: map_fn(top.fn()!) });
            }
            if (top.nullFn() !== undefined) {
                value = Value.from({ nullFn: top.nullFn() === null ? null : map_fn(top.nullFn()!) });
            }
            if (top.arrFn() !== undefined) {
                value = Value.from({ arrFn: map_arr(top.arrFn()!, map_fn) });
            }
            if (top.arrNullFn() !== undefined) {
                value = Value.from({ arrNullFn: map_arr(top.arrNullFn()!, (e) => e === null ? null : map_fn(e)) });
            }
            if (top.objFn() !== undefined) {
                value = Value.from({ objFn: map_obj(top.objFn()!, map_fn) });
            }
            if (top.objNullFn() !== undefined) {
                value = Value.from({ objNullFn: map_obj(top.objNullFn()!, (e) => e === null ? null : map_fn(e)) });
            }
            if (top.sel() !== undefined) {
                value = Value.from({ sel: top.sel() });
            }
            if (top.nullSel() !== undefined) {
                value = Value.from({ nullSel: top.nullSel() });
            }
            if (top.arrSel() !== undefined) {
                value = Value.from({ arrSel: top.arrSel() });
            }
            if (top.arrNullSel() !== undefined) {
                value = Value.from({ arrNullSel: top.arrNullSel() });
            }
            if (top.objSel() !== undefined) {
                value = Value.from({ objSel: top.objSel() });
            }
            if (top.objNullSel() !== undefined) {
                value = Value.from({ objNullSel: top.objNullSel() });
            }
        }

        let output = test.Output.from_Ok_({ value });

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
    return ExStruct.from(args);
} 

function map_union(u: ExUnion): ExUnion {
    var tv = u.getTaggedValue();
    if (tv.tag === 'One') {
        const v1 = tv.value;
        return ExUnion.from_One(ExUnion.One.from({}));
    } else if (tv.tag === 'Two') {
        const v2 = tv.value;
        const args: { required: boolean, optional?: boolean} = {
            required: tv.value.required()
        }
        if (tv.value.optional() !== undefined) {
            args.optional = tv.value.optional();
        }
        return ExUnion.from_Two(args);
    } else {
        const v3 = tv.value;
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
    return example.Input.from(args);
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