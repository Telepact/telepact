#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

import json
from typing import Any, Dict, List, Optional, TypeVar, Callable, Tuple
from telepact_test.gen.all_ import test, Value, ServerHandler_, example as fnexample, getBigList, Undefined, ExUnion, ExStruct


class CodeGenHandler(ServerHandler_):

    async def example(self, headers: dict[str, object], input: fnexample.Input) -> Tuple[dict[str, object], fnexample.Output]:
        raise NotImplementedError("Unimplemented method 'example'")

    async def test(self, headers: dict[str, object], input: test.Input) -> Tuple[dict[str, object], test.Output]:
        ok: test.Output.Ok_ = None

        try:
            print("input: " + json.dumps(input.pseudo_json))
        except json.JSONDecodeError as e:
            print(e)

        if input.value():
            top = input.value()
            if top.bool_() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(bool_=top.bool_()))
            if top.nullBool() != Undefined.Inst:
                print("nullBool: " + str(top.nullBool()))
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(nullBool=top.nullBool()))
            if top.arrBool() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(arrBool=top.arrBool()))
            if top.arrNullBool() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(arrNullBool=top.arrNullBool()))
            if top.objBool() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(objBool=top.objBool()))
            if top.objNullBool() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(objNullBool=top.objNullBool()))
            if top.int_() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(int_=top.int_()))
            if top.nullInt() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(nullInt=top.nullInt()))
            if top.arrInt() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(arrInt=top.arrInt()))
            if top.arrNullInt() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(arrNullInt=top.arrNullInt()))
            if top.objInt() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(objInt=top.objInt()))
            if top.objNullInt() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(objNullInt=top.objNullInt()))
            if top.num() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(num=top.num()))
            if top.nullNum() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(nullNum=top.nullNum()))
            if top.arrNum() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(arrNum=top.arrNum()))
            if top.arrNullNum() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(arrNullNum=top.arrNullNum()))
            if top.objNum() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(objNum=top.objNum()))
            if top.objNullNum() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(objNullNum=top.objNullNum()))
            if top.str_() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(str_=top.str_()))
            if top.nullStr() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(nullStr=top.nullStr()))
            if top.arrStr() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(arrStr=top.arrStr()))
            if top.arrNullStr() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(arrNullStr=top.arrNullStr()))
            if top.objStr() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(objStr=top.objStr()))
            if top.objNullStr() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(objNullStr=top.objNullStr()))
            if top.arr() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(arr=top.arr()))
            if top.nullArr() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(nullArr=top.nullArr()))
            if top.arrArr() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(arrArr=top.arrArr()))
            if top.arrNullArr() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(arrNullArr=top.arrNullArr()))
            if top.objArr() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(objArr=top.objArr()))
            if top.objNullArr() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(objNullArr=top.objNullArr()))
            if top.obj() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(obj=top.obj()))
            if top.nullObj() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(nullObj=top.nullObj()))
            if top.arrObj() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(arrObj=top.arrObj()))
            if top.arrNullObj() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(arrNullObj=top.arrNullObj()))
            if top.objObj() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(objObj=top.objObj()))
            if top.objNullObj() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(objNullObj=top.objNullObj()))
            if top.any() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(any=top.any()))
            if top.nullAny() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(nullAny=top.nullAny()))
            if top.arrAny() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(arrAny=top.arrAny()))
            if top.arrNullAny() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(arrNullAny=top.arrNullAny()))
            if top.objAny() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(objAny=top.objAny()))
            if top.objNullAny() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(objNullAny=top.objNullAny()))
            if top.struct() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(struct=self.map_struct(top.struct())))
            if top.nullStruct() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(nullStruct=self.map_struct(top.nullStruct())))
            if top.arrStruct() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(arrStruct=self.map_arr(top.arrStruct(), self.map_struct)))
            if top.arrNullStruct() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(arrNullStruct=self.map_arr(top.arrNullStruct(), self.map_struct)))
            if top.objStruct() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(objStruct=self.map_obj(top.objStruct(), self.map_struct)))
            if top.objNullStruct() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(objNullStruct=self.map_obj(top.objNullStruct(), self.map_struct)))
            if top.union() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(union=self.map_union(top.union())))
            if top.nullUnion() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(nullUnion=self.map_union(top.nullUnion())))
            if top.arrUnion() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(arrUnion=self.map_arr(top.arrUnion(), self.map_union)))
            if top.arrNullUnion() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(arrNullUnion=self.map_arr(top.arrNullUnion(), self.map_union)))
            if top.objUnion() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(objUnion=self.map_obj(top.objUnion(), self.map_union)))
            if top.objNullUnion() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(objNullUnion=self.map_obj(top.objNullUnion(), self.map_union)))
            if top.fn() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(fn=self.map_fn(top.fn())))
            if top.nullFn() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(nullFn=self.map_fn(top.nullFn())))
            if top.arrFn() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(arrFn=self.map_arr(top.arrFn(), self.map_fn)))
            if top.arrNullFn() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(arrNullFn=self.map_arr(top.arrNullFn(), self.map_fn)))
            if top.objFn() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(objFn=self.map_obj(top.objFn(), self.map_fn)))
            if top.objNullFn() != Undefined.Inst:
                ok = test.Output.Ok_.from_typed(
                    value=Value.from_typed(objNullFn=self.map_obj(top.objNullFn(), self.map_fn)))

        return {}, test.Output.from_Ok_(ok)

    def map_struct(self, s: ExStruct) -> ExStruct:
        if s is None:
            return None
        opt_args = {}
        if s.optional() != Undefined.Inst:
            opt_args["optional"] = s.optional()
        if s.optional2() != Undefined.Inst:
            opt_args["optional2"] = s.optional2()
        return ExStruct.from_typed(required=s.required(), **opt_args)

    def map_union(self, u: ExUnion) -> ExUnion:
        if u is None:
            return None
        tv = u.get_tagged_value()
        if tv.tag == "One":
            return ExUnion.from_One(ExUnion.One.from_typed())
        elif tv.tag == "Two":
            if tv.value.optional() == Undefined.Inst:
                return ExUnion.from_Two(ExUnion.Two.from_typed(
                    required=tv.value.required()
                ))
            else:
                return ExUnion.from_Two(ExUnion.Two.from_typed(
                    required=tv.value.required(),
                    optional=tv.value.optional()
                ))

    def map_fn(self, f: fnexample.Input) -> fnexample.Input:
        if f is None:
            return None
        if f.optional() == Undefined.Inst:
            return fnexample.Input.from_typed(required=f.required())
        else:
            return fnexample.Input.from_typed(required=f.required(), optional=f.optional())

    T = TypeVar('T')

    def map_arr(self, l: list[T], mapper: Callable[[T], T]) -> list[T]:
        if l is None:
            return None
        return [mapper(e) for e in l]

    def map_obj(self, m: dict[str, T], mapper: Callable[[T], T]) -> dict[str, T]:
        if m is None:
            return None
        return {k: mapper(v) for k, v in m.items()}
