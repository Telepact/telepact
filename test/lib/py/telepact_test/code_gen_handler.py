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
import base64
from typing import Any, Dict, List, Optional, TypeVar, Callable, Tuple
from telepact_test.gen.gen_types import test, Value, TypedServer, example as fnexample, getBigList, Undefined, ExUnion, ExStruct
from telepact import Response


class CodeGenHandler(TypedServer):

    async def example(self, headers: dict[str, object], input: fnexample.Input) -> Response:
        raise NotImplementedError("Unimplemented method 'example'")

    async def test(self, headers: dict[str, object], input: test.Input) -> Response:
        try:
            def default_serializer(obj):
                if isinstance(obj, bytes):
                    return base64.b64encode(obj).decode('utf-8')
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

            print("input: " + json.dumps(input.pseudo_json, default=default_serializer))
        except json.JSONDecodeError as e:
            print(e)

        if "@error" in headers and headers["@error"] == True:
            return {}, test.Output.from_ErrorExample2(field1="Boom!")

        ok: test.Output.Ok_ = None

        if input.value():
            top = input.value()
            if top.bool_() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(bool_=top.bool_()))
            if top.nullBool() != Undefined.Inst:
                print("nullBool: " + str(top.nullBool()))
                ok = test.Output.from_Ok_(
                    value=Value.from_(nullBool=top.nullBool()))
            if top.arrBool() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(arrBool=top.arrBool()))
            if top.arrNullBool() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(arrNullBool=top.arrNullBool()))
            if top.objBool() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(objBool=top.objBool()))
            if top.objNullBool() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(objNullBool=top.objNullBool()))
            if top.int_() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(int_=top.int_()))
            if top.nullInt() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(nullInt=top.nullInt()))
            if top.arrInt() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(arrInt=top.arrInt()))
            if top.arrNullInt() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(arrNullInt=top.arrNullInt()))
            if top.objInt() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(objInt=top.objInt()))
            if top.objNullInt() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(objNullInt=top.objNullInt()))
            if top.num() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(num=top.num()))
            if top.nullNum() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(nullNum=top.nullNum()))
            if top.arrNum() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(arrNum=top.arrNum()))
            if top.arrNullNum() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(arrNullNum=top.arrNullNum()))
            if top.objNum() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(objNum=top.objNum()))
            if top.objNullNum() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(objNullNum=top.objNullNum()))
            if top.str_() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(str_=top.str_()))
            if top.nullStr() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(nullStr=top.nullStr()))
            if top.arrStr() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(arrStr=top.arrStr()))
            if top.arrNullStr() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(arrNullStr=top.arrNullStr()))
            if top.objStr() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(objStr=top.objStr()))
            if top.objNullStr() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(objNullStr=top.objNullStr()))
            if top.arr() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(arr=top.arr()))
            # if top.nullArr() != Undefined.Inst:
            #     ok = test.Output.from_Ok_(
            #         value=Value.from_(nullArr=top.nullArr()))
            if top.arrArr() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(arrArr=top.arrArr()))
            # if top.arrNullArr() != Undefined.Inst:
            #     ok = test.Output.from_Ok_(
            #         value=Value.from_(arrNullArr=top.arrNullArr()))
            if top.objArr() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(objArr=top.objArr()))
            # if top.objNullArr() != Undefined.Inst:
            #     ok = test.Output.from_Ok_(
            #         value=Value.from_(objNullArr=top.objNullArr()))
            if top.obj() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(obj=top.obj()))
            # if top.nullObj() != Undefined.Inst:
            #     ok = test.Output.from_Ok_(
            #         value=Value.from_(nullObj=top.nullObj()))
            if top.arrObj() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(arrObj=top.arrObj()))
            # if top.arrNullObj() != Undefined.Inst:
            #     ok = test.Output.from_Ok_(
            #         value=Value.from_(arrNullObj=top.arrNullObj()))
            if top.objObj() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(objObj=top.objObj()))
            # if top.objNullObj() != Undefined.Inst:
            #     ok = test.Output.from_Ok_(
            #         value=Value.from_(objNullObj=top.objNullObj()))
            if top.any() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(any=top.any()))
            if top.nullAny() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(nullAny=top.nullAny()))
            if top.arrAny() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(arrAny=top.arrAny()))
            if top.arrNullAny() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(arrNullAny=top.arrNullAny()))
            if top.objAny() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(objAny=top.objAny()))
            if top.objNullAny() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(objNullAny=top.objNullAny()))
            if top.bytes_() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(bytes_=top.bytes_()))
            if top.nullBytes() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(nullBytes=top.nullBytes()))
            if top.arrBytes() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(arrBytes=top.arrBytes()))
            if top.arrNullBytes() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(arrNullBytes=top.arrNullBytes()))
            if top.objBytes() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(objBytes=top.objBytes()))
            if top.objNullBytes() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(objNullBytes=top.objNullBytes()))
            if top.struct() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(struct=self.map_struct(top.struct())))
            if top.nullStruct() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(nullStruct=self.map_struct(top.nullStruct())))
            if top.arrStruct() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(arrStruct=self.map_arr(top.arrStruct(), self.map_struct)))
            if top.arrNullStruct() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(arrNullStruct=self.map_arr(top.arrNullStruct(), self.map_struct)))
            if top.objStruct() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(objStruct=self.map_obj(top.objStruct(), self.map_struct)))
            if top.objNullStruct() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(objNullStruct=self.map_obj(top.objNullStruct(), self.map_struct)))
            if top.union() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(union=self.map_union(top.union())))
            if top.nullUnion() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(nullUnion=self.map_union(top.nullUnion())))
            if top.arrUnion() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(arrUnion=self.map_arr(top.arrUnion(), self.map_union)))
            if top.arrNullUnion() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(arrNullUnion=self.map_arr(top.arrNullUnion(), self.map_union)))
            if top.objUnion() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(objUnion=self.map_obj(top.objUnion(), self.map_union)))
            if top.objNullUnion() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(objNullUnion=self.map_obj(top.objNullUnion(), self.map_union)))
            if top.fn() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(fn=self.map_fn(top.fn())))
            if top.nullFn() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(nullFn=self.map_fn(top.nullFn())))
            if top.arrFn() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(arrFn=self.map_arr(top.arrFn(), self.map_fn)))
            if top.arrNullFn() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(arrNullFn=self.map_arr(top.arrNullFn(), self.map_fn)))
            if top.objFn() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(objFn=self.map_obj(top.objFn(), self.map_fn)))
            if top.objNullFn() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(objNullFn=self.map_obj(top.objNullFn(), self.map_fn)))
            if top.sel() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(sel=top.sel()))
            if top.nullSel() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(nullSel=top.nullSel()))
            if top.arrSel() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(arrSel=top.arrSel()))
            if top.arrNullSel() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(arrNullSel=top.arrNullSel()))
            if top.objSel() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(objSel=top.objSel()))
            if top.objNullSel() != Undefined.Inst:
                ok = test.Output.from_Ok_(
                    value=Value.from_(objNullSel=top.objNullSel()))

        return {}, ok

    def map_struct(self, s: ExStruct) -> ExStruct:
        if s is None:
            return None
        opt_args = {}
        if s.optional() != Undefined.Inst:
            opt_args["optional"] = s.optional()
        if s.optional2() != Undefined.Inst:
            opt_args["optional2"] = s.optional2()
        return ExStruct.from_(required=s.required(), **opt_args)

    def map_union(self, u: ExUnion) -> ExUnion:
        if u is None:
            return None
        tv = u.get_tagged_value()
        if tv.tag == "One":
            v1 = tv.value
            return ExUnion.from_One()
        elif tv.tag == "Two":
            v2 = tv.value
            if tv.value.optional() == Undefined.Inst:
                return ExUnion.from_Two(
                    required=tv.value.required()
                )
            else:
                return ExUnion.from_Two(
                    required=tv.value.required(),
                    optional=tv.value.optional()
                )
        else:
            v3 = tv.value
            raise ValueError(f"Unknown tag: {tv.tag}")

    def map_fn(self, f: fnexample.Input) -> fnexample.Input:
        if f is None:
            return None
        if f.optional() == Undefined.Inst:
            return fnexample.Input.from_(required=f.required())
        else:
            return fnexample.Input.from_(required=f.required(), optional=f.optional())

    T = TypeVar('T')

    def map_arr(self, l: list[T], mapper: Callable[[T], T]) -> list[T]:
        if l is None:
            return None
        return [mapper(e) for e in l]

    def map_obj(self, m: dict[str, T], mapper: Callable[[T], T]) -> dict[str, T]:
        if m is None:
            return None
        return {k: mapper(v) for k, v in m.items()}
