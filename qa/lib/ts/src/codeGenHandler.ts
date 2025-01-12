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
                value.bool = top.bool;
            }
            if (top.nullBool !== undefined) {
                value.nullBool = top.nullBool;
            }
            if (top.arrBool !== undefined) {
                value.arrBool = top.arrBool;
            }
            if (top.arrNullBool !== undefined) {
                value.arrNullBool = top.arrNullBool;
            }
            if (top.objBool !== undefined) {
                value.objBool = top.objBool;
            }
            if (top.objNullBool !== undefined) {
                value.objNullBool = top.objNullBool;
            }
            if (top.int !== undefined) {
                value.int = top.int;
            }
            if (top.nullInt !== undefined) {
                value.nullInt = top.nullInt;
            }
            if (top.arrInt !== undefined) {
                value.arrInt = top.arrInt;
            }
            if (top.arrNullInt !== undefined) {
                value.arrNullInt = top.arrNullInt;
            }
            if (top.objInt !== undefined) {
                value.objInt = top.objInt;
            }
            if (top.objNullInt !== undefined) {
                value.objNullInt = top.objNullInt;
            }
            if (top.num !== undefined) {
                value.num = top.num;
            }
            if (top.nullNum !== undefined) {
                value.nullNum = top.nullNum;
            }
            if (top.arrNum !== undefined) {
                value.arrNum = top.arrNum;
            }
            if (top.arrNullNum !== undefined) {
                value.arrNullNum = top.arrNullNum;
            }
            if (top.objNum !== undefined) {
                value.objNum = top.objNum;
            }
            if (top.objNullNum !== undefined) {
                value.objNullNum = top.objNullNum;
            }
            if (top.str !== undefined) {
                value.str = top.str;
            }
            if (top.nullStr !== undefined) {
                value.nullStr = top.nullStr;
            }
            if (top.arrStr !== undefined) {
                value.arrStr = top.arrStr;
            }
            if (top.arrNullStr !== undefined) {
                value.arrNullStr = top.arrNullStr;
            }
            if (top.objStr !== undefined) {
                value.objStr = top.objStr;
            }
            if (top.objNullStr !== undefined) {
                value.objNullStr = top.objNullStr;
            }
            if (top.arr !== undefined) {
                value.arr = top.arr;
            }
            if (top.nullArr !== undefined) {
                value.nullArr = top.nullArr;
            }
            if (top.arrArr !== undefined) {
                value.arrArr = top.arrArr;
            }
            if (top.arrNullArr !== undefined) {
                value.arrNullArr = top.arrNullArr;
            }
            if (top.objArr !== undefined) {
                value.objArr = top.objArr;
            }
            if (top.objNullArr !== undefined) {
                value.objNullArr = top.objNullArr;
            }
            if (top.obj !== undefined) {
                value.obj = top.obj;
            }
            if (top.nullObj !== undefined) {
                value.nullObj = top.nullObj;
            }
            if (top.arrObj !== undefined) {
                value.arrObj = top.arrObj;
            }
            if (top.arrNullObj !== undefined) {
                value.arrNullObj = top.arrNullObj;
            }
            if (top.objObj !== undefined) {
                value.objObj = top.objObj;
            }
            if (top.objNullObj !== undefined) {
                value.objNullObj = top.objNullObj;
            }
            if (top.any !== undefined) {
                value.any = top.any;
            }
            if (top.nullAny !== undefined) {
                value.nullAny = top.nullAny;
            }
            if (top.arrAny !== undefined) {
                value.arrAny = top.arrAny;
            }
            if (top.arrNullAny !== undefined) {
                value.arrNullAny = top.arrNullAny;
            }
            if (top.objAny !== undefined) {
                value.objAny = top.objAny;
            }
            if (top.objNullAny !== undefined) {
                value.objNullAny = top.objNullAny;
            }
            if (top.struct !== undefined) {
                value.struct = this.map_struct(top.struct);
            }
            if (top.nullStruct !== undefined) {
                value.nullStruct = top.nullStruct === null ? null : this.map_struct(top.nullStruct);
            }
            if (top.arrStruct !== undefined) {
                value.arrStruct = this.map_arr(top.arrStruct, this.map_struct);
            }
            if (top.arrNullStruct !== undefined) {
                value.arrNullStruct = this.map_arr(top.arrNullStruct, (e) => e === null ? null : this.map_struct(e));
            }
            if (top.objStruct !== undefined) {
                value.objStruct = this.map_obj(top.objStruct, this.map_struct);
            }
            if (top.objNullStruct !== undefined) {
                value.objNullStruct = this.map_obj(top.objNullStruct, (e) => e === null ? null : this.map_struct(e));
            }
            if (top.union !== undefined) {
                value.union = this.map_union(top.union);
            }
            if (top.nullUnion !== undefined) {
                value.nullUnion = top.nullUnion === null ? null : this.map_union(top.nullUnion);
            }
            if (top.arrUnion !== undefined) {
                value.arrUnion = this.map_arr(top.arrUnion, this.map_union);
            }
            if (top.arrNullUnion !== undefined) {
                value.arrNullUnion = this.map_arr(top.arrNullUnion, (e) => e === null ? null : this.map_union(e));
            }
            if (top.objUnion !== undefined) {
                value.objUnion = this.map_obj(top.objUnion, this.map_union);
            }
            if (top.objNullUnion !== undefined) {
                value.objNullUnion = this.map_obj(top.objNullUnion, (e) => e === null ? null : this.map_union(e));
            }
            if (top.fn !== undefined) {
                value.fn = this.map_fn(top.fn);
            }
            if (top.nullFn !== undefined) {
                value.nullFn = top.nullFn === null ? null : this.map_fn(top.nullFn);
            }
            if (top.arrFn !== undefined) {
                value.arrFn = this.map_arr(top.arrFn, this.map_fn);
            }
            if (top.arrNullFn !== undefined) {
                value.arrNullFn = this.map_arr(top.arrNullFn, (e) => e === null ? null : this.map_fn(e));
            }
            if (top.objFn !== undefined) {
                value.objFn = this.map_obj(top.objFn, this.map_fn);
            }
            if (top.objNullFn !== undefined) {
                value.objNullFn = this.map_obj(top.objNullFn, (e) => e === null ? null : this.map_fn(e));
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
