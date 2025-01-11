import { example__Input_, example__Output_, test__Input_, test__Output_, test__Output__Ok_, Value, ServerHandler_, getBigList__Input_, getBigList__Output_, ExUnion__NoMatch_, ExUnion__One, ExUnion__Two, ExUnion, ExStruct } from './gen/all_';

class CodeGenHandler extends ServerHandler_ {

    example(headers: { [key: string]: any }, input: example__Input_): [ { [key: string]: any }, example__Output_ ] {
        throw new Error("Unimplemented method 'example'");
    }

    test(headers: { [key: string]: any }, input: test__Input_): [ { [key: string]: any }, test__Output_ ] {
        const output: {
            value?: Value | undefined,        
        } = {};

        try {
            console.log("input: " + JSON.stringify(input.to_pseudo_json()));
        } catch (e) {
            console.error(e);
        }

        if (input.value) {
            const top = input.value;
            if (top.bool_ !== undefined) {
                output.value = new Value({ bool_: top.bool_ });
            }
            if (top.nullBool !== undefined) {
                output.value = new Value({ nullBool: top.nullBool });
            }
            if (top.arrBool !== undefined) {
                output.value = new Value({ arrBool: top.arrBool });
            }
            if (top.arrNullBool !== undefined) {
                output.value = new Value({ arrNullBool: top.arrNullBool });
            }
            if (top.objBool !== undefined) {
                output.value = new Value({ objBool: top.objBool });
            }
            if (top.objNullBool !== undefined) {
                output.value = new Value({ objNullBool: top.objNullBool });
            }
            if (top.int_ !== undefined) {
                output.value = new Value({ int_: top.int_ });
            }
            if (top.nullInt !== undefined) {
                output.value = new Value({ nullInt: top.nullInt });
            }
            if (top.arrInt !== undefined) {
                output.value = new Value({ arrInt: top.arrInt });
            }
            if (top.arrNullInt !== undefined) {
                output.value = new Value({ arrNullInt: top.arrNullInt });
            }
            if (top.objInt !== undefined) {
                output.value = new Value({ objInt: top.objInt });
            }
            if (top.objNullInt !== undefined) {
                output.value = new Value({ objNullInt: top.objNullInt });
            }
            if (top.num !== undefined) {
                output.value = new Value({ num: top.num });
            }
            if (top.nullNum !== undefined) {
                output.value = new Value({ nullNum: top.nullNum });
            }
            if (top.arrNum !== undefined) {
                output.value = new Value({ arrNum: top.arrNum });
            }
            if (top.arrNullNum !== undefined) {
                output.value = new Value({ arrNullNum: top.arrNullNum });
            }
            if (top.objNum !== undefined) {
                output.value = new Value({ objNum: top.objNum });
            }
            if (top.objNullNum !== undefined) {
                output.value = new Value({ objNullNum: top.objNullNum });
            }
            if (top.str_ !== undefined) {
                output.value = new Value({ str_: top.str_ });
            }
            if (top.nullStr !== undefined) {
                output.value = new Value({ nullStr: top.nullStr });
            }
            if (top.arrStr !== undefined) {
                output.value = new Value({ arrStr: top.arrStr });
            }
            if (top.arrNullStr !== undefined) {
                output.value = new Value({ arrNullStr: top.arrNullStr });
            }
            if (top.objStr !== undefined) {
                output.value = new Value({ objStr: top.objStr });
            }
            if (top.objNullStr !== undefined) {
                output.value = new Value({ objNullStr: top.objNullStr });
            }
            if (top.arr !== undefined) {
                output.value = new Value({ arr: top.arr });
            }
            if (top.nullArr !== undefined) {
                output.value = new Value({ nullArr: top.nullArr });
            }
            if (top.arrArr !== undefined) {
                output.value = new Value({ arrArr: top.arrArr });
            }
            if (top.arrNullArr !== undefined) {
                output.value = new Value({ arrNullArr: top.arrNullArr });
            }
            if (top.objArr !== undefined) {
                output.value = new Value({ objArr: top.objArr });
            }
            if (top.objNullArr !== undefined) {
                output.value = new Value({ objNullArr: top.objNullArr });
            }
            if (top.obj !== undefined) {
                output.value = new Value({ obj: top.obj });
            }
            if (top.nullObj !== undefined) {
                output.value = new Value({ nullObj: top.nullObj });
            }
            if (top.arrObj !== undefined) {
                output.value = new Value({ arrObj: top.arrObj });
            }
            if (top.arrNullObj !== undefined) {
                output.value = new Value({ arrNullObj: top.arrNullObj });
            }
            if (top.objObj !== undefined) {
                output.value = new Value({ objObj: top.objObj });
            }
            if (top.objNullObj !== undefined) {
                output.value = new Value({ objNullObj: top.objNullObj });
            }
            if (top.any !== undefined) {
                output.value = new Value({ any: top.any });
            }
            if (top.nullAny !== undefined) {
                output.value = new Value({ nullAny: top.nullAny });
            }
            if (top.arrAny !== undefined) {
                output.value = new Value({ arrAny: top.arrAny });
            }
            if (top.arrNullAny !== undefined) {
                output.value = new Value({ arrNullAny: top.arrNullAny });
            }
            if (top.objAny !== undefined) {
                output.value = new Value({ objAny: top.objAny });
            }
            if (top.objNullAny !== undefined) {
                output.value = new Value({ objNullAny: top.objNullAny });
            }
            if (top.struct !== undefined) {
                output.value = new Value({ struct: this.map_struct(top.struct) });
            }
            if (top.nullStruct !== undefined) {
                output.value = new Value({ nullStruct: this.map_struct(top.nullStruct) });
            }
            if (top.arrStruct !== undefined) {
                output.value = new Value({ arrStruct: this.map_arr(top.arrStruct, this.map_struct) });
            }
            if (top.arrNullStruct !== undefined) {
                output.value = new Value({ arrNullStruct: this.map_arr(top.arrNullStruct, this.map_struct) });
            }
            if (top.objStruct !== undefined) {
                output.value = new Value({ objStruct: this.map_obj(top.objStruct, this.map_struct) });
            }
            if (top.objNullStruct !== undefined) {
                output.value = new Value({ objNullStruct: this.map_obj(top.objNullStruct, this.map_struct) });
            }
            if (top.union !== undefined) {
                output.value = new Value({ union: this.map_union(top.union) });
            }
            if (top.nullUnion !== undefined) {
                output.value = new Value({ nullUnion: this.map_union(top.nullUnion) });
            }
            if (top.arrUnion !== undefined) {
                output.value = new Value({ arrUnion: this.map_arr(top.arrUnion, this.map_union) });
            }
            if (top.arrNullUnion !== undefined) {
                output.value = new Value({ arrNullUnion: this.map_arr(top.arrNullUnion, this.map_union) });
            }
            if (top.objUnion !== undefined) {
                output.value = new Value({ objUnion: this.map_obj(top.objUnion, this.map_union) });
            }
            if (top.objNullUnion !== undefined) {
                output.value = new Value({ objNullUnion: this.map_obj(top.objNullUnion, this.map_union) });
            }
            if (top.fn !== undefined) {
                output.value = new Value({ fn: this.map_fn(top.fn) });
            }
            if (top.nullFn !== undefined) {
                output.value = new Value({ nullFn: this.map_fn(top.nullFn) });
            }
            if (top.arrFn !== undefined) {
                output.value = new Value({ arrFn: this.map_arr(top.arrFn, this.map_fn) });
            }
            if (top.arrNullFn !== undefined) {
                output.value = new Value({ arrNullFn: this.map_arr(top.arrNullFn, this.map_fn) });
            }
            if (top.objFn !== undefined) {
                output.value = new Value({ objFn: this.map_obj(top.objFn, this.map_fn) });
            }
            if (top.objNullFn !== undefined) {
                output.value = new Value({ objNullFn: this.map_obj(top.objNullFn, this.map_fn) });
            }
        }

        return [{}, new test__Output__Ok_(output)];
    }

    map_struct(s: ExStruct | null): ExStruct | null {
        if (s === null) {
            return null;
        }
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

    map_union(u: ExUnion | null): ExUnion | null {
        if (u === null) {
            return null;
        }
        if (u instanceof ExUnion__NoMatch_) {
            return new ExUnion__NoMatch_();
        } else if (u instanceof ExUnion__One) {
            return new ExUnion__One();
        } else if (u instanceof ExUnion__Two) {
            const b = new ExUnion__Two({
                required: u.required
            });
            if (u.optional !== null) {
                b.optional = u.optional;
            }
            return b;
        }
    }

    map_fn(f: example__Input_ | null): example__Input_ | null {
        if (f === null) {
            return null;
        }
        const b = new example__Input_({
            required: f.required
        });
        if (f.optional !== null) {
            b.optional = f.optional;
        }
        return b;
    }

    map_arr<T>(l: T[], mapper: (item: T) => T): T[] | null {
        if (l === null) {
            return null;
        }
        return l.map(mapper);
    }

    map_obj<T>(m: { [key: string]: T }, mapper: (item: T) => T): { [key: string]: T } | null {
        if (m === null) {
            return null;
        }
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
