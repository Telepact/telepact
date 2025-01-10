type Undefined = undefined;

function utilLet<T, U>(value: T, f: (value: T) => U): U {
    return f(value);
}







    
class Value {
    
        /**
         *  A struct value demonstrating all common type permutations. 
         */
    bool: boolean | Undefined = undefined;
    nullBool: boolean | null | Undefined = undefined;
    arrBool: Array<boolean> | Undefined = undefined;
    arrNullBool: Array<boolean | null> | Undefined = undefined;
    objBool: Record<string, boolean> | Undefined = undefined;
    objNullBool: Record<string, boolean | null> | Undefined = undefined;
    int: number | Undefined = undefined;
    nullInt: number | null | Undefined = undefined;
    arrInt: Array<number> | Undefined = undefined;
    arrNullInt: Array<number | null> | Undefined = undefined;
    objInt: Record<string, number> | Undefined = undefined;
    objNullInt: Record<string, number | null> | Undefined = undefined;
    num: number | Undefined = undefined;
    nullNum: number | null | Undefined = undefined;
    arrNum: Array<number> | Undefined = undefined;
    arrNullNum: Array<number | null> | Undefined = undefined;
    objNum: Record<string, number> | Undefined = undefined;
    objNullNum: Record<string, number | null> | Undefined = undefined;
    str: string | Undefined = undefined;
    nullStr: string | null | Undefined = undefined;
    arrStr: Array<string> | Undefined = undefined;
    arrNullStr: Array<string | null> | Undefined = undefined;
    objStr: Record<string, string> | Undefined = undefined;
    objNullStr: Record<string, string | null> | Undefined = undefined;
    arr: Array<any> | Undefined = undefined;
    nullArr: Array<any> | null | Undefined = undefined;
    arrArr: Array<Array<any>> | Undefined = undefined;
    arrNullArr: Array<Array<any> | null> | Undefined = undefined;
    objArr: Record<string, Array<any>> | Undefined = undefined;
    objNullArr: Record<string, Array<any> | null> | Undefined = undefined;
    obj: Record<string, any> | Undefined = undefined;
    nullObj: Record<string, any> | null | Undefined = undefined;
    arrObj: Array<Record<string, any>> | Undefined = undefined;
    arrNullObj: Array<Record<string, any> | null> | Undefined = undefined;
    objObj: Record<string, Record<string, any>> | Undefined = undefined;
    objNullObj: Record<string, Record<string, any> | null> | Undefined = undefined;
    any: any | Undefined = undefined;
    nullAny: any | null | Undefined = undefined;
    arrAny: Array<any> | Undefined = undefined;
    arrNullAny: Array<any | null> | Undefined = undefined;
    objAny: Record<string, any> | Undefined = undefined;
    objNullAny: Record<string, any | null> | Undefined = undefined;
    struct: ExStruct | Undefined = undefined;
    nullStruct: ExStruct | null | Undefined = undefined;
    arrStruct: Array<ExStruct> | Undefined = undefined;
    arrNullStruct: Array<ExStruct | null> | Undefined = undefined;
    objStruct: Record<string, ExStruct> | Undefined = undefined;
    objNullStruct: Record<string, ExStruct | null> | Undefined = undefined;
    union: ExUnion | Undefined = undefined;
    nullUnion: ExUnion | null | Undefined = undefined;
    arrUnion: Array<ExUnion> | Undefined = undefined;
    arrNullUnion: Array<ExUnion | null> | Undefined = undefined;
    objUnion: Record<string, ExUnion> | Undefined = undefined;
    objNullUnion: Record<string, ExUnion | null> | Undefined = undefined;
    fn: example__Input_ | Undefined = undefined;
    nullFn: example__Input_ | null | Undefined = undefined;
    arrFn: Array<example__Input_> | Undefined = undefined;
    arrNullFn: Array<example__Input_ | null> | Undefined = undefined;
    objFn: Record<string, example__Input_> | Undefined = undefined;
    objNullFn: Record<string, example__Input_ | null> | Undefined = undefined;

    static fromPseudoJson(map_: Record<string, any>): Value {
        const t = new Value();
        t.bool = map_['bool!'] === undefined ? undefined : <boolean>map_["bool!"];
        t.nullBool = map_['nullBool!'] === undefined ? undefined : <boolean | null>map_["nullBool!"];
        t.arrBool = map_['arrBool!'] === undefined ? undefined : utilLet(<Array<boolean>>map_["arrBool!"], d0 => d0.map(e0 => <boolean>e0));
        t.arrNullBool = map_['arrNullBool!'] === undefined ? undefined : utilLet(<Array<boolean | null>>map_["arrNullBool!"], d0 => d0.map(e0 => <boolean | null>e0));
        t.objBool = map_['objBool!'] === undefined ? undefined : utilLet(<Record<string, boolean>>map_["objBool!"], d0 => Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, <boolean>v0])));
        t.objNullBool = map_['objNullBool!'] === undefined ? undefined : utilLet(<Record<string, boolean | null>>map_["objNullBool!"], d0 => Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, <boolean | null>v0])));
        t.int = map_['int!'] === undefined ? undefined : <number>map_["int!"];
        t.nullInt = map_['nullInt!'] === undefined ? undefined : <number | null>map_["nullInt!"];
        t.arrInt = map_['arrInt!'] === undefined ? undefined : utilLet(<Array<number>>map_["arrInt!"], d0 => d0.map(e0 => <number>e0));
        t.arrNullInt = map_['arrNullInt!'] === undefined ? undefined : utilLet(<Array<number | null>>map_["arrNullInt!"], d0 => d0.map(e0 => <number | null>e0));
        t.objInt = map_['objInt!'] === undefined ? undefined : utilLet(<Record<string, number>>map_["objInt!"], d0 => Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, <number>v0])));
        t.objNullInt = map_['objNullInt!'] === undefined ? undefined : utilLet(<Record<string, number | null>>map_["objNullInt!"], d0 => Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, <number | null>v0])));
        t.num = map_['num!'] === undefined ? undefined : <number>map_["num!"];
        t.nullNum = map_['nullNum!'] === undefined ? undefined : <number | null>map_["nullNum!"];
        t.arrNum = map_['arrNum!'] === undefined ? undefined : utilLet(<Array<number>>map_["arrNum!"], d0 => d0.map(e0 => <number>e0));
        t.arrNullNum = map_['arrNullNum!'] === undefined ? undefined : utilLet(<Array<number | null>>map_["arrNullNum!"], d0 => d0.map(e0 => <number | null>e0));
        t.objNum = map_['objNum!'] === undefined ? undefined : utilLet(<Record<string, number>>map_["objNum!"], d0 => Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, <number>v0])));
        t.objNullNum = map_['objNullNum!'] === undefined ? undefined : utilLet(<Record<string, number | null>>map_["objNullNum!"], d0 => Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, <number | null>v0])));
        t.str = map_['str!'] === undefined ? undefined : <string>map_["str!"];
        t.nullStr = map_['nullStr!'] === undefined ? undefined : <string | null>map_["nullStr!"];
        t.arrStr = map_['arrStr!'] === undefined ? undefined : utilLet(<Array<string>>map_["arrStr!"], d0 => d0.map(e0 => <string>e0));
        t.arrNullStr = map_['arrNullStr!'] === undefined ? undefined : utilLet(<Array<string | null>>map_["arrNullStr!"], d0 => d0.map(e0 => <string | null>e0));
        t.objStr = map_['objStr!'] === undefined ? undefined : utilLet(<Record<string, string>>map_["objStr!"], d0 => Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, <string>v0])));
        t.objNullStr = map_['objNullStr!'] === undefined ? undefined : utilLet(<Record<string, string | null>>map_["objNullStr!"], d0 => Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, <string | null>v0])));
        t.arr = map_['arr!'] === undefined ? undefined : utilLet(<Array<any>>map_["arr!"], d0 => d0.map(e0 => <any>e0));
        t.nullArr = map_['nullArr!'] === undefined ? undefined : utilLet(<Array<any> | null>map_["nullArr!"], d0 => d0 === null ? null : d0.map(e0 => <any>e0));
        t.arrArr = map_['arrArr!'] === undefined ? undefined : utilLet(<Array<Array<any>>>map_["arrArr!"], d0 => d0.map(e0 => utilLet(<Array<any>>e0, d1 => d1.map(e1 => <any>e1))));
        t.arrNullArr = map_['arrNullArr!'] === undefined ? undefined : utilLet(<Array<Array<any> | null>>map_["arrNullArr!"], d0 => d0.map(e0 => utilLet(<Array<any> | null>e0, d1 => d1 === null ? null : d1.map(e1 => <any>e1))));
        t.objArr = map_['objArr!'] === undefined ? undefined : utilLet(<Record<string, Array<any>>>map_["objArr!"], d0 => Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, utilLet(<Array<any>>v0, d1 => d1.map(e1 => <any>e1))])));
        t.objNullArr = map_['objNullArr!'] === undefined ? undefined : utilLet(<Record<string, Array<any> | null>>map_["objNullArr!"], d0 => Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, utilLet(<Array<any> | null>v0, d1 => d1 === null ? null : d1.map(e1 => <any>e1))])));
        t.obj = map_['obj!'] === undefined ? undefined : utilLet(<Record<string, any>>map_["obj!"], d0 => Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, <any>v0])));
        t.nullObj = map_['nullObj!'] === undefined ? undefined : utilLet(<Record<string, any> | null>map_["nullObj!"], d0 => d0 === null ? null : Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, <any>v0])));
        t.arrObj = map_['arrObj!'] === undefined ? undefined : utilLet(<Array<Record<string, any>>>map_["arrObj!"], d0 => d0.map(e0 => utilLet(<Record<string, any>>e0, d1 => Object.fromEntries(Object.entries(d1).map(([k1, v1]) => [k1, <any>v1])))));
        t.arrNullObj = map_['arrNullObj!'] === undefined ? undefined : utilLet(<Array<Record<string, any> | null>>map_["arrNullObj!"], d0 => d0.map(e0 => utilLet(<Record<string, any> | null>e0, d1 => d1 === null ? null : Object.fromEntries(Object.entries(d1).map(([k1, v1]) => [k1, <any>v1])))));
        t.objObj = map_['objObj!'] === undefined ? undefined : utilLet(<Record<string, Record<string, any>>>map_["objObj!"], d0 => Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, utilLet(<Record<string, any>>v0, d1 => Object.fromEntries(Object.entries(d1).map(([k1, v1]) => [k1, <any>v1])))])));
        t.objNullObj = map_['objNullObj!'] === undefined ? undefined : utilLet(<Record<string, Record<string, any> | null>>map_["objNullObj!"], d0 => Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, utilLet(<Record<string, any> | null>v0, d1 => d1 === null ? null : Object.fromEntries(Object.entries(d1).map(([k1, v1]) => [k1, <any>v1])))])));
        t.any = map_['any!'] === undefined ? undefined : <any>map_["any!"];
        t.nullAny = map_['nullAny!'] === undefined ? undefined : <any | null>map_["nullAny!"];
        t.arrAny = map_['arrAny!'] === undefined ? undefined : utilLet(<Array<any>>map_["arrAny!"], d0 => d0.map(e0 => <any>e0));
        t.arrNullAny = map_['arrNullAny!'] === undefined ? undefined : utilLet(<Array<any | null>>map_["arrNullAny!"], d0 => d0.map(e0 => <any | null>e0));
        t.objAny = map_['objAny!'] === undefined ? undefined : utilLet(<Record<string, any>>map_["objAny!"], d0 => Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, <any>v0])));
        t.objNullAny = map_['objNullAny!'] === undefined ? undefined : utilLet(<Record<string, any | null>>map_["objNullAny!"], d0 => Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, <any | null>v0])));
        t.struct = map_['struct!'] === undefined ? undefined : utilLet(map_["struct!"], d0 => ExStruct.fromPseudoJson(<Record<string, any>>d0));
        t.nullStruct = map_['nullStruct!'] === undefined ? undefined : utilLet(map_["nullStruct!"], d0 => d0 === null ? null : ExStruct.fromPseudoJson(<Record<string, any>>d0));
        t.arrStruct = map_['arrStruct!'] === undefined ? undefined : utilLet(<Array<ExStruct>>map_["arrStruct!"], d0 => d0.map(e0 => utilLet(e0, d1 => ExStruct.fromPseudoJson(<Record<string, any>>d1))));
        t.arrNullStruct = map_['arrNullStruct!'] === undefined ? undefined : utilLet(<Array<ExStruct | null>>map_["arrNullStruct!"], d0 => d0.map(e0 => utilLet(e0, d1 => d1 === null ? null : ExStruct.fromPseudoJson(<Record<string, any>>d1))));
        t.objStruct = map_['objStruct!'] === undefined ? undefined : utilLet(<Record<string, ExStruct>>map_["objStruct!"], d0 => Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, utilLet(v0, d1 => ExStruct.fromPseudoJson(<Record<string, any>>d1))])));
        t.objNullStruct = map_['objNullStruct!'] === undefined ? undefined : utilLet(<Record<string, ExStruct | null>>map_["objNullStruct!"], d0 => Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, utilLet(v0, d1 => d1 === null ? null : ExStruct.fromPseudoJson(<Record<string, any>>d1))])));
        t.union = map_['union!'] === undefined ? undefined : utilLet(map_["union!"], d0 => ExUnion.fromPseudoJson(<Record<string, any>>d0));
        t.nullUnion = map_['nullUnion!'] === undefined ? undefined : utilLet(map_["nullUnion!"], d0 => d0 === null ? null : ExUnion.fromPseudoJson(<Record<string, any>>d0));
        t.arrUnion = map_['arrUnion!'] === undefined ? undefined : utilLet(<Array<ExUnion>>map_["arrUnion!"], d0 => d0.map(e0 => utilLet(e0, d1 => ExUnion.fromPseudoJson(<Record<string, any>>d1))));
        t.arrNullUnion = map_['arrNullUnion!'] === undefined ? undefined : utilLet(<Array<ExUnion | null>>map_["arrNullUnion!"], d0 => d0.map(e0 => utilLet(e0, d1 => d1 === null ? null : ExUnion.fromPseudoJson(<Record<string, any>>d1))));
        t.objUnion = map_['objUnion!'] === undefined ? undefined : utilLet(<Record<string, ExUnion>>map_["objUnion!"], d0 => Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, utilLet(v0, d1 => ExUnion.fromPseudoJson(<Record<string, any>>d1))])));
        t.objNullUnion = map_['objNullUnion!'] === undefined ? undefined : utilLet(<Record<string, ExUnion | null>>map_["objNullUnion!"], d0 => Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, utilLet(v0, d1 => d1 === null ? null : ExUnion.fromPseudoJson(<Record<string, any>>d1))])));
        t.fn = map_['fn!'] === undefined ? undefined : utilLet(map_["fn!"], d0 => example__Input_.fromPseudoJson(<Record<string, any>>d0));
        t.nullFn = map_['nullFn!'] === undefined ? undefined : utilLet(map_["nullFn!"], d0 => d0 === null ? null : example__Input_.fromPseudoJson(<Record<string, any>>d0));
        t.arrFn = map_['arrFn!'] === undefined ? undefined : utilLet(<Array<example__Input_>>map_["arrFn!"], d0 => d0.map(e0 => utilLet(e0, d1 => example__Input_.fromPseudoJson(<Record<string, any>>d1))));
        t.arrNullFn = map_['arrNullFn!'] === undefined ? undefined : utilLet(<Array<example__Input_ | null>>map_["arrNullFn!"], d0 => d0.map(e0 => utilLet(e0, d1 => d1 === null ? null : example__Input_.fromPseudoJson(<Record<string, any>>d1))));
        t.objFn = map_['objFn!'] === undefined ? undefined : utilLet(<Record<string, example__Input_>>map_["objFn!"], d0 => Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, utilLet(v0, d1 => example__Input_.fromPseudoJson(<Record<string, any>>d1))])));
        t.objNullFn = map_['objNullFn!'] === undefined ? undefined : utilLet(<Record<string, example__Input_ | null>>map_["objNullFn!"], d0 => Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, utilLet(v0, d1 => d1 === null ? null : example__Input_.fromPseudoJson(<Record<string, any>>d1))])));
        return t;
    }

    toPseudoJson(): Record<string, any> {
        const fields: Record<string, any> = {};
        if (this.bool !== undefined) {
            fields["bool!"] = this.bool;
        }
        if (this.nullBool !== undefined) {
            fields["nullBool!"] = this.nullBool;
        }
        if (this.arrBool !== undefined) {
            fields["arrBool!"] = utilLet(this.arrBool, d0 => d0 === null ? null : d0.map(e0 => e0));
        }
        if (this.arrNullBool !== undefined) {
            fields["arrNullBool!"] = utilLet(this.arrNullBool, d0 => d0 === null ? null : d0.map(e0 => e0));
        }
        if (this.objBool !== undefined) {
            fields["objBool!"] = utilLet(this.objBool, d0 => d0 === null ? null : Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, v0])));
        }
        if (this.objNullBool !== undefined) {
            fields["objNullBool!"] = utilLet(this.objNullBool, d0 => d0 === null ? null : Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, v0])));
        }
        if (this.int !== undefined) {
            fields["int!"] = this.int;
        }
        if (this.nullInt !== undefined) {
            fields["nullInt!"] = this.nullInt;
        }
        if (this.arrInt !== undefined) {
            fields["arrInt!"] = utilLet(this.arrInt, d0 => d0 === null ? null : d0.map(e0 => e0));
        }
        if (this.arrNullInt !== undefined) {
            fields["arrNullInt!"] = utilLet(this.arrNullInt, d0 => d0 === null ? null : d0.map(e0 => e0));
        }
        if (this.objInt !== undefined) {
            fields["objInt!"] = utilLet(this.objInt, d0 => d0 === null ? null : Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, v0])));
        }
        if (this.objNullInt !== undefined) {
            fields["objNullInt!"] = utilLet(this.objNullInt, d0 => d0 === null ? null : Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, v0])));
        }
        if (this.num !== undefined) {
            fields["num!"] = this.num;
        }
        if (this.nullNum !== undefined) {
            fields["nullNum!"] = this.nullNum;
        }
        if (this.arrNum !== undefined) {
            fields["arrNum!"] = utilLet(this.arrNum, d0 => d0 === null ? null : d0.map(e0 => e0));
        }
        if (this.arrNullNum !== undefined) {
            fields["arrNullNum!"] = utilLet(this.arrNullNum, d0 => d0 === null ? null : d0.map(e0 => e0));
        }
        if (this.objNum !== undefined) {
            fields["objNum!"] = utilLet(this.objNum, d0 => d0 === null ? null : Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, v0])));
        }
        if (this.objNullNum !== undefined) {
            fields["objNullNum!"] = utilLet(this.objNullNum, d0 => d0 === null ? null : Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, v0])));
        }
        if (this.str !== undefined) {
            fields["str!"] = this.str;
        }
        if (this.nullStr !== undefined) {
            fields["nullStr!"] = this.nullStr;
        }
        if (this.arrStr !== undefined) {
            fields["arrStr!"] = utilLet(this.arrStr, d0 => d0 === null ? null : d0.map(e0 => e0));
        }
        if (this.arrNullStr !== undefined) {
            fields["arrNullStr!"] = utilLet(this.arrNullStr, d0 => d0 === null ? null : d0.map(e0 => e0));
        }
        if (this.objStr !== undefined) {
            fields["objStr!"] = utilLet(this.objStr, d0 => d0 === null ? null : Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, v0])));
        }
        if (this.objNullStr !== undefined) {
            fields["objNullStr!"] = utilLet(this.objNullStr, d0 => d0 === null ? null : Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, v0])));
        }
        if (this.arr !== undefined) {
            fields["arr!"] = utilLet(this.arr, d0 => d0 === null ? null : d0.map(e0 => e0));
        }
        if (this.nullArr !== undefined) {
            fields["nullArr!"] = utilLet(this.nullArr, d0 => d0 === null ? null : d0.map(e0 => e0));
        }
        if (this.arrArr !== undefined) {
            fields["arrArr!"] = utilLet(this.arrArr, d0 => d0 === null ? null : d0.map(e0 => utilLet(e0, d1 => d1 === null ? null : d1.map(e1 => e1))));
        }
        if (this.arrNullArr !== undefined) {
            fields["arrNullArr!"] = utilLet(this.arrNullArr, d0 => d0 === null ? null : d0.map(e0 => utilLet(e0, d1 => d1 === null ? null : d1.map(e1 => e1))));
        }
        if (this.objArr !== undefined) {
            fields["objArr!"] = utilLet(this.objArr, d0 => d0 === null ? null : Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, utilLet(v0, d1 => d1 === null ? null : d1.map(e1 => e1))])));
        }
        if (this.objNullArr !== undefined) {
            fields["objNullArr!"] = utilLet(this.objNullArr, d0 => d0 === null ? null : Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, utilLet(v0, d1 => d1 === null ? null : d1.map(e1 => e1))])));
        }
        if (this.obj !== undefined) {
            fields["obj!"] = utilLet(this.obj, d0 => d0 === null ? null : Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, v0])));
        }
        if (this.nullObj !== undefined) {
            fields["nullObj!"] = utilLet(this.nullObj, d0 => d0 === null ? null : Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, v0])));
        }
        if (this.arrObj !== undefined) {
            fields["arrObj!"] = utilLet(this.arrObj, d0 => d0 === null ? null : d0.map(e0 => utilLet(e0, d1 => d1 === null ? null : Object.fromEntries(Object.entries(d1).map(([k1, v1]) => [k1, v1])))));
        }
        if (this.arrNullObj !== undefined) {
            fields["arrNullObj!"] = utilLet(this.arrNullObj, d0 => d0 === null ? null : d0.map(e0 => utilLet(e0, d1 => d1 === null ? null : Object.fromEntries(Object.entries(d1).map(([k1, v1]) => [k1, v1])))));
        }
        if (this.objObj !== undefined) {
            fields["objObj!"] = utilLet(this.objObj, d0 => d0 === null ? null : Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, utilLet(v0, d1 => d1 === null ? null : Object.fromEntries(Object.entries(d1).map(([k1, v1]) => [k1, v1])))])));
        }
        if (this.objNullObj !== undefined) {
            fields["objNullObj!"] = utilLet(this.objNullObj, d0 => d0 === null ? null : Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, utilLet(v0, d1 => d1 === null ? null : Object.fromEntries(Object.entries(d1).map(([k1, v1]) => [k1, v1])))])));
        }
        if (this.any !== undefined) {
            fields["any!"] = this.any;
        }
        if (this.nullAny !== undefined) {
            fields["nullAny!"] = this.nullAny;
        }
        if (this.arrAny !== undefined) {
            fields["arrAny!"] = utilLet(this.arrAny, d0 => d0 === null ? null : d0.map(e0 => e0));
        }
        if (this.arrNullAny !== undefined) {
            fields["arrNullAny!"] = utilLet(this.arrNullAny, d0 => d0 === null ? null : d0.map(e0 => e0));
        }
        if (this.objAny !== undefined) {
            fields["objAny!"] = utilLet(this.objAny, d0 => d0 === null ? null : Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, v0])));
        }
        if (this.objNullAny !== undefined) {
            fields["objNullAny!"] = utilLet(this.objNullAny, d0 => d0 === null ? null : Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, v0])));
        }
        if (this.struct !== undefined) {
            fields["struct!"] = utilLet(this.struct, d0 => d0 === null ? null : d0.toPseudoJson());
        }
        if (this.nullStruct !== undefined) {
            fields["nullStruct!"] = utilLet(this.nullStruct, d0 => d0 === null ? null : d0.toPseudoJson());
        }
        if (this.arrStruct !== undefined) {
            fields["arrStruct!"] = utilLet(this.arrStruct, d0 => d0 === null ? null : d0.map(e0 => utilLet(e0, d1 => d1 === null ? null : d1.toPseudoJson())));
        }
        if (this.arrNullStruct !== undefined) {
            fields["arrNullStruct!"] = utilLet(this.arrNullStruct, d0 => d0 === null ? null : d0.map(e0 => utilLet(e0, d1 => d1 === null ? null : d1.toPseudoJson())));
        }
        if (this.objStruct !== undefined) {
            fields["objStruct!"] = utilLet(this.objStruct, d0 => d0 === null ? null : Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, utilLet(v0, d1 => d1 === null ? null : d1.toPseudoJson())])));
        }
        if (this.objNullStruct !== undefined) {
            fields["objNullStruct!"] = utilLet(this.objNullStruct, d0 => d0 === null ? null : Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, utilLet(v0, d1 => d1 === null ? null : d1.toPseudoJson())])));
        }
        if (this.union !== undefined) {
            fields["union!"] = utilLet(this.union, d0 => d0 === null ? null : d0.toPseudoJson());
        }
        if (this.nullUnion !== undefined) {
            fields["nullUnion!"] = utilLet(this.nullUnion, d0 => d0 === null ? null : d0.toPseudoJson());
        }
        if (this.arrUnion !== undefined) {
            fields["arrUnion!"] = utilLet(this.arrUnion, d0 => d0 === null ? null : d0.map(e0 => utilLet(e0, d1 => d1 === null ? null : d1.toPseudoJson())));
        }
        if (this.arrNullUnion !== undefined) {
            fields["arrNullUnion!"] = utilLet(this.arrNullUnion, d0 => d0 === null ? null : d0.map(e0 => utilLet(e0, d1 => d1 === null ? null : d1.toPseudoJson())));
        }
        if (this.objUnion !== undefined) {
            fields["objUnion!"] = utilLet(this.objUnion, d0 => d0 === null ? null : Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, utilLet(v0, d1 => d1 === null ? null : d1.toPseudoJson())])));
        }
        if (this.objNullUnion !== undefined) {
            fields["objNullUnion!"] = utilLet(this.objNullUnion, d0 => d0 === null ? null : Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, utilLet(v0, d1 => d1 === null ? null : d1.toPseudoJson())])));
        }
        if (this.fn !== undefined) {
            fields["fn!"] = utilLet(this.fn, d0 => d0 === null ? null : d0.toPseudoJson());
        }
        if (this.nullFn !== undefined) {
            fields["nullFn!"] = utilLet(this.nullFn, d0 => d0 === null ? null : d0.toPseudoJson());
        }
        if (this.arrFn !== undefined) {
            fields["arrFn!"] = utilLet(this.arrFn, d0 => d0 === null ? null : d0.map(e0 => utilLet(e0, d1 => d1 === null ? null : d1.toPseudoJson())));
        }
        if (this.arrNullFn !== undefined) {
            fields["arrNullFn!"] = utilLet(this.arrNullFn, d0 => d0 === null ? null : d0.map(e0 => utilLet(e0, d1 => d1 === null ? null : d1.toPseudoJson())));
        }
        if (this.objFn !== undefined) {
            fields["objFn!"] = utilLet(this.objFn, d0 => d0 === null ? null : Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, utilLet(v0, d1 => d1 === null ? null : d1.toPseudoJson())])));
        }
        if (this.objNullFn !== undefined) {
            fields["objNullFn!"] = utilLet(this.objNullFn, d0 => d0 === null ? null : Object.fromEntries(Object.entries(d0).map(([k0, v0]) => [k0, utilLet(v0, d1 => d1 === null ? null : d1.toPseudoJson())])));
        }
        return fields;
    }
}



    
class ExStruct {
    
        /**
         *  The main struct example.                                                        
         *                                                                                  
         *  The [required] field must be supplied. The optional field does not need to be   
         *  supplied.                                                                       
         */
    required: boolean;
    optional: boolean | Undefined = undefined;
    optional2: number | Undefined = undefined;

    static fromPseudoJson(map_: Record<string, any>): ExStruct {
        const t = new ExStruct();
        t.required = <boolean>map_["required"];
        t.optional = map_['optional!'] === undefined ? undefined : <boolean>map_["optional!"];
        t.optional2 = map_['optional2!'] === undefined ? undefined : <number>map_["optional2!"];
        return t;
    }

    toPseudoJson(): Record<string, any> {
        const fields: Record<string, any> = {};
        fields["required"] = this.required;
        if (this.optional !== undefined) {
            fields["optional!"] = this.optional;
        }
        if (this.optional2 !== undefined) {
            fields["optional2!"] = this.optional2;
        }
        return fields;
    }
}



    

abstract class ExUnion {
    

    static fromPseudoJson(map_: Record<string, any>): ExUnion {
        const entry = Object.entries(map_)[0]!;
        const case_name = entry[0];
        const payload = <Record<string, any>>entry[1];
        if (case_name === "NoMatch_") {
            return <ExUnion>ExUnion__NoMatch_.fromPseudoJson(payload);
        }
            
        else if (case_name === "One") {
            return <ExUnion>ExUnion__One.fromPseudoJson(payload);
        }
            
        else if (case_name === "Two") {
            return <ExUnion>ExUnion__Two.fromPseudoJson(payload);
        }
        else {
            return <ExUnion>ExUnion__NoMatch_.fromPseudoJson(payload);
        }
    }

    abstract toPseudoJson(): Record<string, any>;
}


class ExUnion__NoMatch_ implements ExUnion {
    

    static fromPseudoJson(map_: Record<string, any>): ExUnion__NoMatch_ {
        const t = new ExUnion__NoMatch_();
        return t;
    }

    toPseudoJson(): Record<string, any> {
        const fields: Record<string, any> = {};
        return {
            "NoMatch_": fields
        };
    }
}

    
    
    
class ExUnion__One implements ExUnion {
    

    static fromPseudoJson(map_: Record<string, any>): ExUnion__One {
        const t = new ExUnion__One();
        return t;
    }

    toPseudoJson(): Record<string, any> {
        const fields: Record<string, any> = {};
        return {
            "One": fields
        };
    }
}

    
    
    
class ExUnion__Two implements ExUnion {
    
    required: boolean;
    optional: boolean | Undefined = undefined;

    static fromPseudoJson(map_: Record<string, any>): ExUnion__Two {
        const t = new ExUnion__Two();
        t.required = <boolean>map_["required"];
        t.optional = map_['optional!'] === undefined ? undefined : <boolean>map_["optional!"];
        return t;
    }

    toPseudoJson(): Record<string, any> {
        const fields: Record<string, any> = {};
        fields["required"] = this.required;
        if (this.optional !== undefined) {
            fields["optional!"] = this.optional;
        }
        return {
            "Two": fields
        };
    }
}




    
class Big {
    
    aF: boolean;
    cF: boolean;
    bF: boolean;
    dF: boolean;

    static fromPseudoJson(map_: Record<string, any>): Big {
        const t = new Big();
        t.aF = <boolean>map_["aF"];
        t.cF = <boolean>map_["cF"];
        t.bF = <boolean>map_["bF"];
        t.dF = <boolean>map_["dF"];
        return t;
    }

    toPseudoJson(): Record<string, any> {
        const fields: Record<string, any> = {};
        fields["aF"] = this.aF;
        fields["cF"] = this.cF;
        fields["bF"] = this.bF;
        fields["dF"] = this.dF;
        return fields;
    }
}



    
        
    

    
class example__Input_ {
    
    required: boolean;
    optional: boolean | Undefined = undefined;

    static fromPseudoJson(map_init: Record<string, any>): example__Input_ {
        const map_ = <Record<string, any>>map_init["fn.example"];
        const t = new example__Input_();
        t.required = <boolean>map_["required"];
        t.optional = map_['optional!'] === undefined ? undefined : <boolean>map_["optional!"];
        return t;
    }

    toPseudoJson(): Record<string, any> {
        const fields: Record<string, any> = {};
        fields["required"] = this.required;
        if (this.optional !== undefined) {
            fields["optional!"] = this.optional;
        }
        return {
            "fn.example": fields
        };
    }
}


    

abstract class example__Output_ {
    

    static fromPseudoJson(map_: Record<string, any>): example__Output_ {
        const entry = Object.entries(map_)[0];
        const case_name = entry[0];
        const payload = <Record<string, any>>entry[1];
        if (case_name === "NoMatch_") {
            return <example__Output_>example__Output__NoMatch_.fromPseudoJson(payload);
        }
            
        else if (case_name === "Ok_") {
            return <example__Output_>example__Output__Ok_.fromPseudoJson(payload);
        }
        else {
            return <example__Output_>example__Output__NoMatch_.fromPseudoJson(payload);
        }
    }

    abstract toPseudoJson(): Record<string, any>;
}


class example__Output__NoMatch_ implements example__Output_ {
    

    static fromPseudoJson(map_init: Record<string, any>): example__Output__NoMatch_ {
        const map_ = <Record<string, any>>map_init["NoMatch_"];
        const t = new example__Output__NoMatch_();
        return t;
    }

    toPseudoJson(): Record<string, any> {
        const fields: Record<string, any> = {};
        return {
            "NoMatch_": fields
        };
    }
}

    
    
    
class example__Output__Ok_ implements example__Output_ {
    
    required: boolean;
    optional: boolean | Undefined = undefined;

    static fromPseudoJson(map_init: Record<string, any>): example__Output__Ok_ {
        const map_ = <Record<string, any>>map_init["Ok_"];
        const t = new example__Output__Ok_();
        t.required = <boolean>map_["required"];
        t.optional = map_['optional!'] === undefined ? undefined : <boolean>map_["optional!"];
        return t;
    }

    toPseudoJson(): Record<string, any> {
        const fields: Record<string, any> = {};
        fields["required"] = this.required;
        if (this.optional !== undefined) {
            fields["optional!"] = this.optional;
        }
        return {
            "Ok_": fields
        };
    }
}





    
        
    

    
class test__Input_ {
    
    value: Value | Undefined = undefined;

    static fromPseudoJson(map_init: Record<string, any>): test__Input_ {
        const map_ = <Record<string, any>>map_init["fn.test"];
        const t = new test__Input_();
        t.value = map_['value!'] === undefined ? undefined : utilLet(map_["value!"], d0 => Value.fromPseudoJson(<Record<string, any>>d0));
        return t;
    }

    toPseudoJson(): Record<string, any> {
        const fields: Record<string, any> = {};
        if (this.value !== undefined) {
            fields["value!"] = utilLet(this.value, d0 => d0 === null ? null : d0.toPseudoJson());
        }
        return {
            "fn.test": fields
        };
    }
}


    

abstract class test__Output_ {
    

    static fromPseudoJson(map_: Record<string, any>): test__Output_ {
        const entry = Object.entries(map_)[0];
        const case_name = entry[0];
        const payload = <Record<string, any>>entry[1];
        if (case_name === "NoMatch_") {
            return <test__Output_>test__Output__NoMatch_.fromPseudoJson(payload);
        }
            
        else if (case_name === "Ok_") {
            return <test__Output_>test__Output__Ok_.fromPseudoJson(payload);
        }
            
        else if (case_name === "ErrorExample") {
            return <test__Output_>test__Output__ErrorExample.fromPseudoJson(payload);
        }
        else {
            return <test__Output_>test__Output__NoMatch_.fromPseudoJson(payload);
        }
    }

    abstract toPseudoJson(): Record<string, any>;
}


class test__Output__NoMatch_ implements test__Output_ {
    

    static fromPseudoJson(map_init: Record<string, any>): test__Output__NoMatch_ {
        const map_ = <Record<string, any>>map_init["NoMatch_"];
        const t = new test__Output__NoMatch_();
        return t;
    }

    toPseudoJson(): Record<string, any> {
        const fields: Record<string, any> = {};
        return {
            "NoMatch_": fields
        };
    }
}

    
    
    
class test__Output__Ok_ implements test__Output_ {
    
    value: Value | Undefined = undefined;

    static fromPseudoJson(map_init: Record<string, any>): test__Output__Ok_ {
        const map_ = <Record<string, any>>map_init["Ok_"];
        const t = new test__Output__Ok_();
        t.value = map_['value!'] === undefined ? undefined : utilLet(map_["value!"], d0 => Value.fromPseudoJson(<Record<string, any>>d0));
        return t;
    }

    toPseudoJson(): Record<string, any> {
        const fields: Record<string, any> = {};
        if (this.value !== undefined) {
            fields["value!"] = utilLet(this.value, d0 => d0 === null ? null : d0.toPseudoJson());
        }
        return {
            "Ok_": fields
        };
    }
}

    
    
    
class test__Output__ErrorExample implements test__Output_ {
    
    property: string;

    static fromPseudoJson(map_init: Record<string, any>): test__Output__ErrorExample {
        const map_ = <Record<string, any>>map_init["ErrorExample"];
        const t = new test__Output__ErrorExample();
        t.property = <string>map_["property"];
        return t;
    }

    toPseudoJson(): Record<string, any> {
        const fields: Record<string, any> = {};
        fields["property"] = this.property;
        return {
            "ErrorExample": fields
        };
    }
}





    
        
    

    
class getBigList__Input_ {
    

    static fromPseudoJson(map_init: Record<string, any>): getBigList__Input_ {
        const map_ = <Record<string, any>>map_init["fn.getBigList"];
        const t = new getBigList__Input_();
        return t;
    }

    toPseudoJson(): Record<string, any> {
        const fields: Record<string, any> = {};
        return {
            "fn.getBigList": fields
        };
    }
}


    

abstract class getBigList__Output_ {
    

    static fromPseudoJson(map_: Record<string, any>): getBigList__Output_ {
        const entry = Object.entries(map_)[0];
        const case_name = entry[0];
        const payload = <Record<string, any>>entry[1];
        if (case_name === "NoMatch_") {
            return <getBigList__Output_>getBigList__Output__NoMatch_.fromPseudoJson(payload);
        }
            
        else if (case_name === "Ok_") {
            return <getBigList__Output_>getBigList__Output__Ok_.fromPseudoJson(payload);
        }
        else {
            return <getBigList__Output_>getBigList__Output__NoMatch_.fromPseudoJson(payload);
        }
    }

    abstract toPseudoJson(): Record<string, any>;
}


class getBigList__Output__NoMatch_ implements getBigList__Output_ {
    

    static fromPseudoJson(map_init: Record<string, any>): getBigList__Output__NoMatch_ {
        const map_ = <Record<string, any>>map_init["NoMatch_"];
        const t = new getBigList__Output__NoMatch_();
        return t;
    }

    toPseudoJson(): Record<string, any> {
        const fields: Record<string, any> = {};
        return {
            "NoMatch_": fields
        };
    }
}

    
    
    
class getBigList__Output__Ok_ implements getBigList__Output_ {
    
    items: Array<Big>;

    static fromPseudoJson(map_init: Record<string, any>): getBigList__Output__Ok_ {
        const map_ = <Record<string, any>>map_init["Ok_"];
        const t = new getBigList__Output__Ok_();
        t.items = utilLet(<Array<Big>>map_["items"], d0 => d0.map(e0 => utilLet(e0, d1 => Big.fromPseudoJson(<Record<string, any>>d1))));
        return t;
    }

    toPseudoJson(): Record<string, any> {
        const fields: Record<string, any> = {};
        fields["items"] = utilLet(this.items, d0 => d0 === null ? null : d0.map(e0 => utilLet(e0, d1 => d1 === null ? null : d1.toPseudoJson())));
        return {
            "Ok_": fields
        };
    }
}





import * as uapi from 'uapi';

class ClientInterface_ {

    client: uapi.Client.Client;

    constructor(client: uapi.Client.Client) {
        this.client = client;
    }

    
    example(headers: Record<string, any>, input: example__Input_): example__Output_ {
        const message = this.client.request(new uapi.Message.Message(headers, input.toPseudoJson()));
        return example__Output_.fromPseudoJson(message.body);
    }
    test(headers: Record<string, any>, input: test__Input_): test__Output_ {
        const message = this.client.request(new uapi.Message.Message(headers, input.toPseudoJson()));
        return test__Output_.fromPseudoJson(message.body);
    }
    getBigList(headers: Record<string, any>, input: getBigList__Input_): getBigList__Output_ {
        const message = this.client.request(new uapi.Message.Message(headers, input.toPseudoJson()));
        return getBigList__Output_.fromPseudoJson(message.body);
    }
}

class ServerHandler_ {

    
    example(headers: Record<string, any>, input: example__Input_): example__Output_ {
        throw new Error("Not implemented");
    }
    test(headers: Record<string, any>, input: test__Input_): test__Output_ {
        throw new Error("Not implemented");
    }
    getBigList(headers: Record<string, any>, input: getBigList__Input_): getBigList__Output_ {
        throw new Error("Not implemented");
    }

    handler(message: uapi.Message.Message): uapi.Message.Message {
        const function_name = Object.keys(message.body)[0];

        
        
        if (function_name === "fn.example") {
            const output = this.example(message.header, example__Input_.fromPseudoJson(message.body));
            return new uapi.Message.Message({}, output.toPseudoJson());
        }
        
        
        
        else if (function_name === "fn.test") {
            const output = this.test(message.header, test__Input_.fromPseudoJson(message.body));
            return new uapi.Message.Message({}, output.toPseudoJson());
        }
        
        
        
        else if (function_name === "fn.getBigList") {
            const output = this.getBigList(message.header, getBigList__Input_.fromPseudoJson(message.body));
            return new uapi.Message.Message({}, output.toPseudoJson());
        }
        
        

        throw new Error("Unknown function: " + function_name);
    }
}