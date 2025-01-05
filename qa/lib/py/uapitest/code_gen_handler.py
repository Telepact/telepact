import json
from typing import Any, Dict, List, Optional, TypeVar, Callable
from uapitest.gen.all_ import example as fn_example, test, Value, ExStruct, ExUnion, ServerHandler_, getBigList


class CodeGenHandler(ServerHandler_):

    def example(self, headers: dict[str, object], input: fn_example.Input) -> fn_example.Output:
        raise NotImplementedError("Unimplemented method 'example'")

    def test(self, headers: dict[str, object], input: test.Input) -> test.Output:
        output = test.Output.Ok_()

        a: bool = 'a'

        try:
            print("input: " + json.dumps(input.to_pseudo_json()))
        except json.JSONDecodeError as e:
            print(e)

        if input.value:
            top = input.value
            if top.bool:
                output.value = Value(bool=top.bool)
            if top.nullBool:
                output.value = Value(nullBool=top.nullBool)
            if top.arrBool:
                output.value = Value(arrBool=top.arrBool)
            if top.arrNullBool:
                output.value = Value(arrNullBool=top.arrNullBool)
            if top.objBool:
                output.value = Value(objBool=top.objBool)
            if top.objNullBool:
                output.value = Value(objNullBool=top.objNullBool)
            if top.int:
                output.value = Value(int=top.int)
            if top.nullInt:
                output.value = Value(nullInt=top.nullInt)
            if top.arrInt:
                output.value = Value(arrInt=top.arrInt)
            if top.arrNullInt:
                output.value = Value(arrNullInt=top.arrNullInt)
            if top.objInt:
                output.value = Value(objInt=top.objInt)
            if top.objNullInt:
                output.value = Value(objNullInt=top.objNullInt)
            if top.num:
                output.value = Value(num=top.num)
            if top.nullNum:
                output.value = Value(nullNum=top.nullNum)
            if top.arrNum:
                output.value = Value(arrNum=top.arrNum)
            if top.arrNullNum:
                output.value = Value(arrNullNum=top.arrNullNum)
            if top.objNum:
                output.value = Value(objNum=top.objNum)
            if top.objNullNum:
                output.value = Value(objNullNum=top.objNullNum)
            if top.str:
                output.value = Value(str=top.str)
            if top.nullStr:
                output.value = Value(nullStr=top.nullStr)
            if top.arrStr:
                output.value = Value(arrStr=top.arrStr)
            if top.arrNullStr:
                output.value = Value(arrNullStr=top.arrNullStr)
            if top.objStr:
                output.value = Value(objStr=top.objStr)
            if top.objNullStr:
                output.value = Value(objNullStr=top.objNullStr)
            if top.arr:
                output.value = Value(arr=top.arr)
            if top.nullArr:
                output.value = Value(nullArr=top.nullArr)
            if top.arrArr:
                output.value = Value(arrArr=top.arrArr)
            if top.arrNullArr:
                output.value = Value(arrNullArr=top.arrNullArr)
            if top.objArr:
                output.value = Value(objArr=top.objArr)
            if top.objNullArr:
                output.value = Value(objNullArr=top.objNullArr)
            if top.obj:
                output.value = Value(obj=top.obj)
            if top.nullObj:
                output.value = Value(nullObj=top.nullObj)
            if top.arrObj:
                output.value = Value(arrObj=top.arrObj)
            if top.arrNullObj:
                output.value = Value(arrNullObj=top.arrNullObj)
            if top.objObj:
                output.value = Value(objObj=top.objObj)
            if top.objNullObj:
                output.value = Value(objNullObj=top.objNullObj)
            if top.any:
                output.value = Value(any=top.any)
            if top.nullAny:
                output.value = Value(nullAny=top.nullAny)
            if top.arrAny:
                output.value = Value(arrAny=top.arrAny)
            if top.arrNullAny:
                output.value = Value(arrNullAny=top.arrNullAny)
            if top.objAny:
                output.value = Value(objAny=top.objAny)
            if top.objNullAny:
                output.value = Value(objNullAny=top.objNullAny)
            if top.struct:
                output.value = Value(struct=self.map_struct(top.struct))
            if top.nullStruct:
                output.value = Value(
                    nullStruct=self.map_struct(top.nullStruct))
            if top.arrStruct:
                output.value = Value(arrStruct=self.map_arr(
                    top.arrStruct, self.map_struct))
            if top.arrNullStruct:
                output.value = Value(arrNullStruct=self.map_arr(
                    top.arrNullStruct, self.map_struct))
            if top.objStruct:
                output.value = Value(objStruct=self.map_obj(
                    top.objStruct, self.map_struct))
            if top.objNullStruct:
                output.value = Value(objNullStruct=self.map_obj(
                    top.objNullStruct, self.map_struct))
            if top.union:
                output.value = Value(union=self.map_union(top.union))
            if top.nullUnion:
                output.value = Value(nullUnion=self.map_union(top.nullUnion))
            if top.arrUnion:
                output.value = Value(arrUnion=self.map_arr(
                    top.arrUnion, self.map_union))
            if top.arrNullUnion:
                output.value = Value(arrNullUnion=self.map_arr(
                    top.arrNullUnion, self.map_union))
            if top.objUnion:
                output.value = Value(objUnion=self.map_obj(
                    top.objUnion, self.map_union))
            if top.objNullUnion:
                output.value = Value(objNullUnion=self.map_obj(
                    top.objNullUnion, self.map_union))
            if top.fn:
                output.value = Value(fn=self.map_fn(top.fn))
            if top.nullFn:
                output.value = Value(nullFn=self.map_fn(top.nullFn))
            if top.arrFn:
                output.value = Value(
                    arrFn=self.map_arr(top.arrFn, self.map_fn))
            if top.arrNullFn:
                output.value = Value(arrNullFn=self.map_arr(
                    top.arrNullFn, self.map_fn))
            if top.objFn:
                output.value = Value(
                    objFn=self.map_obj(top.objFn, self.map_fn))
            if top.objNullFn:
                output.value = Value(objNullFn=self.map_obj(
                    top.objNullFn, self.map_fn))

        return output

    def map_struct(self, s: ExStruct) -> ExStruct:
        if s is None:
            return None
        b = ExStruct()
        b.required = s.required
        if s.optional:
            b.optional = s.optional
        if s.optional2:
            b.optional2 = s.optional2
        return b

    def map_union(self, u: ExUnion) -> ExUnion:
        if u is None:
            return None
        if isinstance(u, ExUnion.NoMatch_):
            return ExUnion.NoMatch_(ExUnion.NoMatch_())
        elif isinstance(u, ExUnion.One):
            return ExUnion.One()
        elif isinstance(u, ExUnion.Two):
            b = ExUnion.Two()
            b.required = u.required
            if u.optional:
                b.optional = u.optional
            return b

    def map_fn(self, f: fn_example.Input) -> fn_example.Input:
        if f is None:
            return None
        b = fn_example.Input()
        if f.optional:
            b.optional = f.optional
        b.required = f.required
        return b

    T = TypeVar('T')

    def map_arr(l: list[T], mapper: Callable[[T], T]) -> list[T]:
        if l is None:
            return None
        return [mapper(e) for e in l]

    def map_obj(m: dict[str, T], mapper: Callable[[T], T]) -> dict[str, T]:
        if m is None:
            return None
        return {k: mapper(v) for k, v in m.items()}

    def get_big_list(self, headers: dict[str, object], input: getBigList.Input) -> getBigList.Output:
        raise NotImplementedError("Unimplemented method 'getBigList'")
