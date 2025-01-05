import json
from typing import Any, Dict, List, Optional, TypeVar, Callable
from uapitest.gen.all_ import example as fn_example, test, Value, ExStruct, ExUnion, ServerHandler_, getBigList, Undefined


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
            if not isinstance(top.bool, Undefined):
                output.value = Value(bool=top.bool)
            if not isinstance(top.nullBool, Undefined):
                output.value = Value(nullBool=top.nullBool)
            if not isinstance(top.arrBool, Undefined):
                output.value = Value(arrBool=top.arrBool)
            if not isinstance(top.arrNullBool, Undefined):
                output.value = Value(arrNullBool=top.arrNullBool)
            if not isinstance(top.objBool, Undefined):
                output.value = Value(objBool=top.objBool)
            if not isinstance(top.objNullBool, Undefined):
                output.value = Value(objNullBool=top.objNullBool)
            if not isinstance(top.int, Undefined):
                output.value = Value(int=top.int)
            if not isinstance(top.nullInt, Undefined):
                output.value = Value(nullInt=top.nullInt)
            if not isinstance(top.arrInt, Undefined):
                output.value = Value(arrInt=top.arrInt)
            if not isinstance(top.arrNullInt, Undefined):
                output.value = Value(arrNullInt=top.arrNullInt)
            if not isinstance(top.objInt, Undefined):
                output.value = Value(objInt=top.objInt)
            if not isinstance(top.objNullInt, Undefined):
                output.value = Value(objNullInt=top.objNullInt)
            if not isinstance(top.num, Undefined):
                output.value = Value(num=top.num)
            if not isinstance(top.nullNum, Undefined):
                output.value = Value(nullNum=top.nullNum)
            if not isinstance(top.arrNum, Undefined):
                output.value = Value(arrNum=top.arrNum)
            if not isinstance(top.arrNullNum, Undefined):
                output.value = Value(arrNullNum=top.arrNullNum)
            if not isinstance(top.objNum, Undefined):
                output.value = Value(objNum=top.objNum)
            if not isinstance(top.objNullNum, Undefined):
                output.value = Value(objNullNum=top.objNullNum)
            if not isinstance(top.str, Undefined):
                output.value = Value(str=top.str)
            if not isinstance(top.nullStr, Undefined):
                output.value = Value(nullStr=top.nullStr)
            if not isinstance(top.arrStr, Undefined):
                output.value = Value(arrStr=top.arrStr)
            if not isinstance(top.arrNullStr, Undefined):
                output.value = Value(arrNullStr=top.arrNullStr)
            if not isinstance(top.objStr, Undefined):
                output.value = Value(objStr=top.objStr)
            if not isinstance(top.objNullStr, Undefined):
                output.value = Value(objNullStr=top.objNullStr)
            if not isinstance(top.arr, Undefined):
                output.value = Value(arr=top.arr)
            if not isinstance(top.nullArr, Undefined):
                output.value = Value(nullArr=top.nullArr)
            if not isinstance(top.arrArr, Undefined):
                output.value = Value(arrArr=top.arrArr)
            if not isinstance(top.arrNullArr, Undefined):
                output.value = Value(arrNullArr=top.arrNullArr)
            if not isinstance(top.objArr, Undefined):
                output.value = Value(objArr=top.objArr)
            if not isinstance(top.objNullArr, Undefined):
                output.value = Value(objNullArr=top.objNullArr)
            if not isinstance(top.obj, Undefined):
                output.value = Value(obj=top.obj)
            if not isinstance(top.nullObj, Undefined):
                output.value = Value(nullObj=top.nullObj)
            if not isinstance(top.arrObj, Undefined):
                output.value = Value(arrObj=top.arrObj)
            if not isinstance(top.arrNullObj, Undefined):
                output.value = Value(arrNullObj=top.arrNullObj)
            if not isinstance(top.objObj, Undefined):
                output.value = Value(objObj=top.objObj)
            if not isinstance(top.objNullObj, Undefined):
                output.value = Value(objNullObj=top.objNullObj)
            if not isinstance(top.any, Undefined):
                output.value = Value(any=top.any)
            if not isinstance(top.nullAny, Undefined):
                output.value = Value(nullAny=top.nullAny)
            if not isinstance(top.arrAny, Undefined):
                output.value = Value(arrAny=top.arrAny)
            if not isinstance(top.arrNullAny, Undefined):
                output.value = Value(arrNullAny=top.arrNullAny)
            if not isinstance(top.objAny, Undefined):
                output.value = Value(objAny=top.objAny)
            if not isinstance(top.objNullAny, Undefined):
                output.value = Value(objNullAny=top.objNullAny)
            if not isinstance(top.struct, Undefined):
                output.value = Value(struct=self.map_struct(top.struct))
            if not isinstance(top.nullStruct, Undefined):
                output.value = Value(
                    nullStruct=self.map_struct(top.nullStruct))
            if not isinstance(top.arrStruct, Undefined):
                output.value = Value(arrStruct=self.map_arr(
                    top.arrStruct, self.map_struct))
            if not isinstance(top.arrNullStruct, Undefined):
                output.value = Value(arrNullStruct=self.map_arr(
                    top.arrNullStruct, self.map_struct))
            if not isinstance(top.objStruct, Undefined):
                output.value = Value(objStruct=self.map_obj(
                    top.objStruct, self.map_struct))
            if not isinstance(top.objNullStruct, Undefined):
                output.value = Value(objNullStruct=self.map_obj(
                    top.objNullStruct, self.map_struct))
            if not isinstance(top.union, Undefined):
                output.value = Value(union=self.map_union(top.union))
            if not isinstance(top.nullUnion, Undefined):
                output.value = Value(nullUnion=self.map_union(top.nullUnion))
            if not isinstance(top.arrUnion, Undefined):
                output.value = Value(arrUnion=self.map_arr(
                    top.arrUnion, self.map_union))
            if not isinstance(top.arrNullUnion, Undefined):
                output.value = Value(arrNullUnion=self.map_arr(
                    top.arrNullUnion, self.map_union))
            if not isinstance(top.objUnion, Undefined):
                output.value = Value(objUnion=self.map_obj(
                    top.objUnion, self.map_union))
            if not isinstance(top.objNullUnion, Undefined):
                output.value = Value(objNullUnion=self.map_obj(
                    top.objNullUnion, self.map_union))
            if not isinstance(top.fn, Undefined):
                output.value = Value(fn=self.map_fn(top.fn))
            if not isinstance(top.nullFn, Undefined):
                output.value = Value(nullFn=self.map_fn(top.nullFn))
            if not isinstance(top.arrFn, Undefined):
                output.value = Value(
                    arrFn=self.map_arr(top.arrFn, self.map_fn))
            if not isinstance(top.arrNullFn, Undefined):
                output.value = Value(arrNullFn=self.map_arr(
                    top.arrNullFn, self.map_fn))
            if not isinstance(top.objFn, Undefined):
                output.value = Value(
                    objFn=self.map_obj(top.objFn, self.map_fn))
            if not isinstance(top.objNullFn, Undefined):
                output.value = Value(objNullFn=top.objNullFn)
                output.value = Value(objNullFn=self.map_obj(
                    top.objNullFn, self.map_fn))

        return output

    def map_struct(self, s: ExStruct) -> ExStruct:
        if s is None:
            return None
        b = ExStruct(
            required=s.required
        )
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
        b = fn_example.Input(required=f.required)
        if f.optional:
            b.optional = f.optional
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
