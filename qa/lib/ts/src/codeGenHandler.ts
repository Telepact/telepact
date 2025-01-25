import { example__Input_, example__Output_, test__Input_, test__Output_, test__Output__Ok_, Value, ServerHandler_, getBigList__Input_, getBigList__Output_, ExUnion__NoMatch_, ExUnion__One, ExUnion__Two, ExUnion, ExStruct } from './gen/all_.js';

export class CodeGenHandler extends ServerHandler_ {

    example(headers: { [key: string]: any }, input: example__Input_): [ { [key: string]: any }, example__Output_ ] {
        throw new Error("Unimplemented method 'example'");
    }

    test(headers: { [key: string]: any }, input: test__Input_): [ { [key: string]: any }, test__Output_ ] {
        let value = new Value({});

        try {
            console.log("input: " + JSON.stringify(input.toPseudoJson()));
        } catch (e) {
            console.error(e);
        }

        if (input.value) {
            const top = input.value;
            if (top.bool !== undefined) {
                value = Value.fromTyped({ bool: top.bool });
            }
            if (top.nullBool !== undefined) {
                value = Value.fromTyped({ nullBool: top.nullBool });
            }
            if (top.arrBool !== undefined) {
                value = Value.fromTyped({ arrBool: top.arrBool });
            }
            if (top.arrNullBool !== undefined) {
                value = Value.fromTyped({ arrNullBool: top.arrNullBool });
            }
            if (top.objBool !== undefined) {
                value = Value.fromTyped({ objBool: top.objBool });
            }
            if (top.objNullBool !== undefined) {
                value = Value.fromTyped({ objNullBool: top.objNullBool });
            }
            if (top.int !== undefined) {
                value = Value.fromTyped({ int: top.int });
            }
            if (top.nullInt !== undefined) {
                value = Value.fromTyped({ nullInt: top.nullInt });
            }
            if (top.arrInt !== undefined) {
                value = Value.fromTyped({ arrInt: top.arrInt });
            }
            if (top.arrNullInt !== undefined) {
                value = Value.fromTyped({ arrNullInt: top.arrNullInt });
            }
            if (top.objInt !== undefined) {
                value = Value.fromTyped({ objInt: top.objInt });
            }
            if (top.objNullInt !== undefined) {
                value = Value.fromTyped({ objNullInt: top.objNullInt });
            }
            if (top.num !== undefined) {
                value = Value.fromTyped({ num: top.num });
            }
            if (top.nullNum !== undefined) {
                value = Value.fromTyped({ nullNum: top.nullNum });
            }
            if (top.arrNum !== undefined) {
                value = Value.fromTyped({ arrNum: top.arrNum });
            }
            if (top.arrNullNum !== undefined) {
                value = Value.fromTyped({ arrNullNum: top.arrNullNum });
            }
            if (top.objNum !== undefined) {
                value = Value.fromTyped({ objNum: top.objNum });
            }
            if (top.objNullNum !== undefined) {
                value = Value.fromTyped({ objNullNum: top.objNullNum });
            }
            if (top.str !== undefined) {
                value = Value.fromTyped({ str: top.str });
            }
            if (top.nullStr !== undefined) {
                value = Value.fromTyped({ nullStr: top.nullStr });
            }
            if (top.arrStr !== undefined) {
                value = Value.fromTyped({ arrStr: top.arrStr });
            }
            if (top.arrNullStr !== undefined) {
                value = Value.fromTyped({ arrNullStr: top.arrNullStr });
            }
            if (top.objStr !== undefined) {
                value = Value.fromTyped({ objStr: top.objStr });
            }
            if (top.objNullStr !== undefined) {
                value = Value.fromTyped({ objNullStr: top.objNullStr });
            }
            if (top.arr !== undefined) {
                value = Value.fromTyped({ arr: top.arr });
            }
            if (top.nullArr !== undefined) {
                value = Value.fromTyped({ nullArr: top.nullArr });
            }
            if (top.arrArr !== undefined) {
                value = Value.fromTyped({ arrArr: top.arrArr });
            }
            if (top.arrNullArr !== undefined) {
                value = Value.fromTyped({ arrNullArr: top.arrNullArr });
            }
            if (top.objArr !== undefined) {
                value = Value.fromTyped({ objArr: top.objArr });
            }
            if (top.objNullArr !== undefined) {
                value = Value.fromTyped({ objNullArr: top.objNullArr });
            }
            if (top.obj !== undefined) {
                value = Value.fromTyped({ obj: top.obj });
            }
            if (top.nullObj !== undefined) {
                value = Value.fromTyped({ nullObj: top.nullObj });
            }
            if (top.arrObj !== undefined) {
                value = Value.fromTyped({ arrObj: top.arrObj });
            }
            if (top.arrNullObj !== undefined) {
                value = Value.fromTyped({ arrNullObj: top.arrNullObj });
            }
            if (top.objObj !== undefined) {
                value = Value.fromTyped({ objObj: top.objObj });
            }
            if (top.objNullObj !== undefined) {
                value = Value.fromTyped({ objNullObj: top.objNullObj });
            }
            if (top.any !== undefined) {
                value = Value.fromTyped({ any: top.any });
            }
            if (top.nullAny !== undefined) {
                value = Value.fromTyped({ nullAny: top.nullAny });
            }
            if (top.arrAny !== undefined) {
                value = Value.fromTyped({ arrAny: top.arrAny });
            }
            if (top.arrNullAny !== undefined) {
                value = Value.fromTyped({ arrNullAny: top.arrNullAny });
            }
            if (top.objAny !== undefined) {
                value = Value.fromTyped({ objAny: top.objAny });
            }
            if (top.objNullAny !== undefined) {
                value = Value.fromTyped({ objNullAny: top.objNullAny });
            }
            if (top.struct !== undefined) {
                value = Value.fromTyped({ struct: this.map_struct(top.struct) });
            }
            if (top.nullStruct !== undefined) {
                value = Value.fromTyped({ nullStruct: top.nullStruct === null ? null : this.map_struct(top.nullStruct) });
            }
            if (top.arrStruct !== undefined) {
                value = Value.fromTyped({ arrStruct: this.map_arr(top.arrStruct, this.map_struct) });
            }
            if (top.arrNullStruct !== undefined) {
                value = Value.fromTyped({ arrNullStruct: this.map_arr(top.arrNullStruct, (e) => e === null ? null : this.map_struct(e)) });
            }
            if (top.objStruct !== undefined) {
                value = Value.fromTyped({ objStruct: this.map_obj(top.objStruct, this.map_struct) });
            }
            if (top.objNullStruct !== undefined) {
                value = Value.fromTyped({ objNullStruct: this.map_obj(top.objNullStruct, (e) => e === null ? null : this.map_struct(e)) });
            }
            if (top.union !== undefined) {
                value = Value.fromTyped({ union: this.map_union(top.union) });
            }
            if (top.nullUnion !== undefined) {
                value = Value.fromTyped({ nullUnion: top.nullUnion === null ? null : this.map_union(top.nullUnion) });
            }
            if (top.arrUnion !== undefined) {
                value = Value.fromTyped({ arrUnion: this.map_arr(top.arrUnion, this.map_union) });
            }
            if (top.arrNullUnion !== undefined) {
                value = Value.fromTyped({ arrNullUnion: this.map_arr(top.arrNullUnion, (e) => e === null ? null : this.map_union(e)) });
            }
            if (top.objUnion !== undefined) {
                value = Value.fromTyped({ objUnion: this.map_obj(top.objUnion, this.map_union) });
            }
            if (top.objNullUnion !== undefined) {
                value = Value.fromTyped({ objNullUnion: this.map_obj(top.objNullUnion, (e) => e === null ? null : this.map_union(e)) });
            }
            if (top.fn !== undefined) {
                value = Value.fromTyped({ fn: this.map_fn(top.fn) });
            }
            if (top.nullFn !== undefined) {
                value = Value.fromTyped({ nullFn: top.nullFn === null ? null : this.map_fn(top.nullFn) });
            }
            if (top.arrFn !== undefined) {
                value = Value.fromTyped({ arrFn: this.map_arr(top.arrFn, this.map_fn) });
            }
            if (top.arrNullFn !== undefined) {
                value = Value.fromTyped({ arrNullFn: this.map_arr(top.arrNullFn, (e) => e === null ? null : this.map_fn(e)) });
            }
            if (top.objFn !== undefined) {
                value = Value.fromTyped({ objFn: this.map_obj(top.objFn, this.map_fn) });
            }
            if (top.objNullFn !== undefined) {
                value = Value.fromTyped({ objNullFn: this.map_obj(top.objNullFn, (e) => e === null ? null : this.map_fn(e)) });
            }
        }

        return [{}, new test__Output__Ok_({ value: value })];
    }

    map_struct(s: ExStruct): ExStruct {
        const b = new ExStruct({
            required: s.required
        });
        if (s.optional !== null) {
            b.optional = s.optional;
        }
        if (s.optional2 !== null) {
            b.optional2 = s.optional2;
        }
        return b;
    } 

    map_union(u: ExUnion): ExUnion {
        if (u instanceof ExUnion__NoMatch_) {
            return new ExUnion__NoMatch_({});
        } else if (u instanceof ExUnion__One) {
            return new ExUnion__One({});
        } else if (u instanceof ExUnion__Two) {
            const b = new ExUnion__Two({
                required: u.required
            });
            if (u.optional !== null) {
                b.optional = u.optional;
            }
            return b;
        } else {
            throw new Error("Unknown union type: " + u.constructor.name);
        }
    }

    map_fn(f: example__Input_): example__Input_ {
        const b = new example__Input_({
            required: f.required
        });
        if (f.optional !== null) {
            b.optional = f.optional;
        }
        return b;
    }

    map_arr<T>(l: T[], mapper: (item: T) => T): T[] {
        return l.map(mapper);
    }

    map_obj<T>(m: { [key: string]: T }, mapper: (item: T) => T): { [key: string]: T } {
        const result: { [key: string]: T } = {};
        for (const key in m) {
            if (m.hasOwnProperty(key)) {
                result[key] = mapper(m[key]!);
            }
        }
        return result;
    }

    get_big_list(headers: { [key: string]: any }, input: getBigList__Input_): getBigList__Output_ {
        throw new Error("Unimplemented method 'getBigList'");
    }
}
