import json
from typing import Any, Dict, List, Optional, TypeVar, Callable, Tuple
from uapitest.gen.all_ import test, Value, ServerHandler_, example as fnexample, getBigList, Undefined, ExUnion, ExStruct


class CodeGenHandler(ServerHandler_):

    async def example(self, headers: dict[str, object], input: fnexample.Input) -> Tuple[dict[str, object], example.Output]:
        raise NotImplementedError("Unimplemented method 'example'")

    async def test(self, headers: dict[str, object], input: test.Input) -> Tuple[dict[str, object], test.Output]:
        output = test.Output.Ok_()

        try:
            print("input: " + json.dumps(input.to_pseudo_json()))
        except json.JSONDecodeError as e:
            print(e)

        if input.value():
            top = input.value()
            if not isinstance(top.bool_(), Undefined):
                output = test.Output.Ok_.from_typed(value=top.bool_())
            if not isinstance(top.nullBool(), Undefined):
                output = test.Output.Ok_.from_typed(nullBool=top.nullBool())
            if not isinstance(top.arrBool(), Undefined):
                output = test.Output.Ok_.from_typed(arrBool=top.arrBool())
            if not isinstance(top.arrNullBool(), Undefined):
                output = test.Output.Ok_.from_typed(
                    arrNullBool=top.arrNullBool())
            if not isinstance(top.objBool(), Undefined):
                output = test.Output.Ok_.from_typed(objBool=top.objBool())
            if not isinstance(top.objNullBool(), Undefined):
                output = test.Output.Ok_.from_typed(
                    objNullBool=top.objNullBool())
            if not isinstance(top.int_(), Undefined):
                output = test.Output.Ok_.from_typed(int_=top.int_())
            if not isinstance(top.nullInt(), Undefined):
                output = test.Output.Ok_.from_typed(nullInt=top.nullInt())
            if not isinstance(top.arrInt(), Undefined):
                output = test.Output.Ok_.from_typed(arrInt=top.arrInt())
            if not isinstance(top.arrNullInt(), Undefined):
                output = test.Output.Ok_.from_typed(
                    arrNullInt=top.arrNullInt())
            if not isinstance(top.objInt(), Undefined):
                output = test.Output.Ok_.from_typed(objInt=top.objInt())
            if not isinstance(top.objNullInt(), Undefined):
                output = test.Output.Ok_.from_typed(
                    objNullInt=top.objNullInt())
            if not isinstance(top.num(), Undefined):
                output = test.Output.Ok_.from_typed(num=top.num())
            if not isinstance(top.nullNum(), Undefined):
                output = test.Output.Ok_.from_typed(nullNum=top.nullNum())
            if not isinstance(top.arrNum(), Undefined):
                output = test.Output.Ok_.from_typed(arrNum=top.arrNum())
            if not isinstance(top.arrNullNum(), Undefined):
                output = test.Output.Ok_.from_typed(
                    arrNullNum=top.arrNullNum())
            if not isinstance(top.objNum(), Undefined):
                output = test.Output.Ok_.from_typed(objNum=top.objNum())
            if not isinstance(top.objNullNum(), Undefined):
                output = test.Output.Ok_.from_typed(
                    objNullNum=top.objNullNum())
            if not isinstance(top.str_(), Undefined):
                output = test.Output.Ok_.from_typed(str_=top.str_())
            if not isinstance(top.nullStr(), Undefined):
                output = test.Output.Ok_.from_typed(nullStr=top.nullStr())
            if not isinstance(top.arrStr(), Undefined):
                output = test.Output.Ok_.from_typed(arrStr=top.arrStr())
            if not isinstance(top.arrNullStr(), Undefined):
                output = test.Output.Ok_.from_typed(
                    arrNullStr=top.arrNullStr())
            if not isinstance(top.objStr(), Undefined):
                output = test.Output.Ok_.from_typed(objStr=top.objStr())
            if not isinstance(top.objNullStr(), Undefined):
                output = test.Output.Ok_.from_typed(
                    objNullStr=top.objNullStr())
            if not isinstance(top.arr(), Undefined):
                output = test.Output.Ok_.from_typed(arr=top.arr())
            if not isinstance(top.nullArr(), Undefined):
                output = test.Output.Ok_.from_typed(nullArr=top.nullArr())
            if not isinstance(top.arrArr(), Undefined):
                output = test.Output.Ok_.from_typed(arrArr=top.arrArr())
            if not isinstance(top.arrNullArr(), Undefined):
                output = test.Output.Ok_.from_typed(
                    arrNullArr=top.arrNullArr())
            if not isinstance(top.objArr(), Undefined):
                output = test.Output.Ok_.from_typed(objArr=top.objArr())
            if not isinstance(top.objNullArr(), Undefined):
                output = test.Output.Ok_.from_typed(
                    objNullArr=top.objNullArr())
            if not isinstance(top.obj(), Undefined):
                output = test.Output.Ok_.from_typed(obj=top.obj())
            if not isinstance(top.nullObj(), Undefined):
                output = test.Output.Ok_.from_typed(nullObj=top.nullObj())
            if not isinstance(top.arrObj(), Undefined):
                output = test.Output.Ok_.from_typed(arrObj=top.arrObj())
            if not isinstance(top.arrNullObj(), Undefined):
                output = test.Output.Ok_.from_typed(
                    arrNullObj=top.arrNullObj())
            if not isinstance(top.objObj(), Undefined):
                output = test.Output.Ok_.from_typed(objObj=top.objObj())
            if not isinstance(top.objNullObj(), Undefined):
                output = test.Output.Ok_.from_typed(
                    objNullObj=top.objNullObj())
            if not isinstance(top.any(), Undefined):
                output = test.Output.Ok_.from_typed(any=top.any())
            if not isinstance(top.nullAny(), Undefined):
                output = test.Output.Ok_.from_typed(nullAny=top.nullAny())
            if not isinstance(top.arrAny(), Undefined):
                output = test.Output.Ok_.from_typed(arrAny=top.arrAny())
            if not isinstance(top.arrNullAny(), Undefined):
                output = test.Output.Ok_.from_typed(
                    arrNullAny=top.arrNullAny())
            if not isinstance(top.objAny(), Undefined):
                output = test.Output.Ok_.from_typed(objAny=top.objAny())
            if not isinstance(top.objNullAny(), Undefined):
                output = test.Output.Ok_.from_typed(
                    objNullAny=top.objNullAny())
            if not isinstance(top.struct(), Undefined):
                output = test.Output.Ok_.from_typed(
                    struct=self.map_struct(top.struct()))
            if not isinstance(top.nullStruct(), Undefined):
                output = test.Output.Ok_.from_typed(
                    nullStruct=self.map_struct(top.nullStruct()))
            if not isinstance(top.arrStruct(), Undefined):
                output = test.Output.Ok_.from_typed(
                    arrStruct=self.map_arr(top.arrStruct(), self.map_struct))
            if not isinstance(top.arrNullStruct(), Undefined):
                output = test.Output.Ok_.from_typed(
                    arrNullStruct=self.map_arr(top.arrNullStruct(), self.map_struct))
            if not isinstance(top.objStruct(), Undefined):
                output = test.Output.Ok_.from_typed(
                    objStruct=self.map_obj(top.objStruct(), self.map_struct))
            if not isinstance(top.objNullStruct(), Undefined):
                output = test.Output.Ok_.from_typed(
                    objNullStruct=self.map_obj(top.objNullStruct(), self.map_struct))
            if not isinstance(top.union(), Undefined):
                output = test.Output.Ok_.from_typed(
                    union=self.map_union(top.union()))
            if not isinstance(top.nullUnion(), Undefined):
                output = test.Output.Ok_.from_typed(
                    nullUnion=self.map_union(top.nullUnion()))
            if not isinstance(top.arrUnion(), Undefined):
                output = test.Output.Ok_.from_typed(
                    arrUnion=self.map_arr(top.arrUnion(), self.map_union))
            if not isinstance(top.arrNullUnion(), Undefined):
                output = test.Output.Ok_.from_typed(
                    arrNullUnion=self.map_arr(top.arrNullUnion(), self.map_union))
            if not isinstance(top.objUnion(), Undefined):
                output = test.Output.Ok_.from_typed(
                    objUnion=self.map_obj(top.objUnion(), self.map_union))
            if not isinstance(top.objNullUnion(), Undefined):
                output = test.Output.Ok_.from_typed(
                    objNullUnion=self.map_obj(top.objNullUnion(), self.map_union))
            if not isinstance(top.fn(), Undefined):
                output = test.Output.Ok_.from_typed(fn=self.map_fn(top.fn()))
            if not isinstance(top.nullFn(), Undefined):
                output = test.Output.Ok_.from_typed(
                    nullFn=self.map_fn(top.nullFn()))
            if not isinstance(top.arrFn(), Undefined):
                output = test.Output.Ok_.from_typed(
                    arrFn=self.map_arr(top.arrFn(), self.map_fn))
            if not isinstance(top.arrNullFn(), Undefined):
                output = test.Output.Ok_.from_typed(
                    arrNullFn=self.map_arr(top.arrNullFn(), self.map_fn))
            if not isinstance(top.objFn(), Undefined):
                output = test.Output.Ok_.from_typed(
                    objFn=self.map_obj(top.objFn(), self.map_fn))
            if not isinstance(top.objNullFn(), Undefined):
                output = test.Output.Ok_.from_typed(
                    objNullFn=self.map_obj(top.objNullFn(), self.map_fn))

        return {}, output

    def map_struct(self, s: ExStruct) -> ExStruct:
        if s is None:
            return None
        if isinstance(s.optional(), Undefined):
            return ExStruct(required=s.required())
        else:
            return ExStruct(required=s.required(), optional=s.optional())

    def map_union(self, u: ExUnion) -> ExUnion:
        if u is None:
            return None
        tv = u.get_tagged_value()
        if tv.tag == "One":
            return ExUnion.One.from_typed()
        elif tv.tag == "Two":
            if isinstance(tv.value, Undefined):
                return ExUnion.Two.from_typed(
                    required=tv.value.required()
                )
            else:
                return ExUnion.Two.from_typed(
                    required=tv.value.required(),
                    optional=tv.value.optional()
                )

    def map_fn(self, f: fnexample.Input) -> fnexample.Input:
        if f is None:
            return None
        if isinstance(f.optional(), Undefined):
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
