import json
from typing import Any, Dict, List, Optional, TypeVar, Callable, Tuple
from uapitest.gen.all_ import example__Input_, example__Output_, test__Input_, test__Output_, test__Output__Ok_, Value, ServerHandler_, getBigList__Input_, getBigList__Output_, Undefined, ExUnion__NoMatch_, ExUnion__One, ExUnion__Two, ExUnion, ExStruct


class CodeGenHandler(ServerHandler_):

    async def example(self, headers: dict[str, object], input: example__Input_) -> Tuple[dict[str, object], example__Output_]:
        raise NotImplementedError("Unimplemented method 'example'")

    async def test(self, headers: dict[str, object], input: test__Input_) -> Tuple[dict[str, object], test__Output_]:
        output = test__Output__Ok_()

        try:
            print("input: " + json.dumps(input.to_pseudo_json()))
        except json.JSONDecodeError as e:
            print(e)

        if input.value():
            top = input.value()
            if not isinstance(top.bool(), Undefined):
                output.value = Value.from_typed(bool=top.bool())
            if not isinstance(top.nullBool(), Undefined):
                output.value = Value.from_typed(nullBool=top.nullBool())
            if not isinstance(top.arrBool(), Undefined):
                output.value = Value.from_typed(arrBool=top.arrBool())
            if not isinstance(top.arrNullBool(), Undefined):
                output.value = Value.from_typed(arrNullBool=top.arrNullBool())
            if not isinstance(top.objBool(), Undefined):
                output.value = Value.from_typed(objBool=top.objBool())
            if not isinstance(top.objNullBool(), Undefined):
                output.value = Value.from_typed(objNullBool=top.objNullBool())
            if not isinstance(top.int_(), Undefined):
                output.value = Value.from_typed(int_=top.int_())
            if not isinstance(top.nullInt(), Undefined):
                output.value = Value.from_typed(nullInt=top.nullInt())
            if not isinstance(top.arrInt(), Undefined):
                output.value = Value.from_typed(arrInt=top.arrInt())
            if not isinstance(top.arrNullInt(), Undefined):
                output.value = Value.from_typed(arrNullInt=top.arrNullInt())
            if not isinstance(top.objInt(), Undefined):
                output.value = Value.from_typed(objInt=top.objInt())
            if not isinstance(top.objNullInt(), Undefined):
                output.value = Value.from_typed(objNullInt=top.objNullInt())
            if not isinstance(top.num(), Undefined):
                output.value = Value.from_typed(num=top.num())
            if not isinstance(top.nullNum(), Undefined):
                output.value = Value.from_typed(nullNum=top.nullNum())
            if not isinstance(top.arrNum(), Undefined):
                output.value = Value.from_typed(arrNum=top.arrNum())
            if not isinstance(top.arrNullNum(), Undefined):
                output.value = Value.from_typed(arrNullNum=top.arrNullNum())
            if not isinstance(top.objNum(), Undefined):
                output.value = Value.from_typed(objNum=top.objNum())
            if not isinstance(top.objNullNum(), Undefined):
                output.value = Value.from_typed(objNullNum=top.objNullNum())
            if not isinstance(top.str_(), Undefined):
                output.value = Value.from_typed(str_=top.str_())
            if not isinstance(top.nullStr(), Undefined):
                output.value = Value.from_typed(nullStr=top.nullStr())
            if not isinstance(top.arrStr(), Undefined):
                output.value = Value.from_typed(arrStr=top.arrStr())
            if not isinstance(top.arrNullStr(), Undefined):
                output.value = Value.from_typed(arrNullStr=top.arrNullStr())
            if not isinstance(top.objStr(), Undefined):
                output.value = Value.from_typed(objStr=top.objStr())
            if not isinstance(top.objNullStr(), Undefined):
                output.value = Value.from_typed(objNullStr=top.objNullStr())
            if not isinstance(top.arr(), Undefined):
                output.value = Value.from_typed(arr=top.arr())
            if not isinstance(top.nullArr(), Undefined):
                output.value = Value.from_typed(nullArr=top.nullArr())
            if not isinstance(top.arrArr(), Undefined):
                output.value = Value.from_typed(arrArr=top.arrArr())
            if not isinstance(top.arrNullArr(), Undefined):
                output.value = Value.from_typed(arrNullArr=top.arrNullArr())
            if not isinstance(top.objArr(), Undefined):
                output.value = Value.from_typed(objArr=top.objArr())
            if not isinstance(top.objNullArr(), Undefined):
                output.value = Value.from_typed(objNullArr=top.objNullArr())
            if not isinstance(top.obj(), Undefined):
                output.value = Value.from_typed(obj=top.obj())
            if not isinstance(top.nullObj(), Undefined):
                output.value = Value.from_typed(nullObj=top.nullObj())
            if not isinstance(top.arrObj(), Undefined):
                output.value = Value.from_typed(arrObj=top.arrObj())
            if not isinstance(top.arrNullObj(), Undefined):
                output.value = Value.from_typed(arrNullObj=top.arrNullObj())
            if not isinstance(top.objObj(), Undefined):
                output.value = Value.from_typed(objObj=top.objObj())
            if not isinstance(top.objNullObj(), Undefined):
                output.value = Value.from_typed(objNullObj=top.objNullObj())
            if not isinstance(top.any(), Undefined):
                output.value = Value.from_typed(any=top.any())
            if not isinstance(top.nullAny(), Undefined):
                output.value = Value.from_typed(nullAny=top.nullAny())
            if not isinstance(top.arrAny(), Undefined):
                output.value = Value.from_typed(arrAny=top.arrAny())
            if not isinstance(top.arrNullAny(), Undefined):
                output.value = Value.from_typed(arrNullAny=top.arrNullAny())
            if not isinstance(top.objAny(), Undefined):
                output.value = Value.from_typed(objAny=top.objAny())
            if not isinstance(top.objNullAny(), Undefined):
                output.value = Value.from_typed(objNullAny=top.objNullAny())
            if not isinstance(top.struct(), Undefined):
                output.value = Value.from_typed(
                    struct=self.map_struct(top.struct()))
            if not isinstance(top.nullStruct(), Undefined):
                output.value = Value.from_typed(
                    nullStruct=self.map_struct(top.nullStruct()))
            if not isinstance(top.arrStruct(), Undefined):
                output.value = Value.from_typed(
                    arrStruct=self.map_arr(top.arrStruct(), self.map_struct))
            if not isinstance(top.arrNullStruct(), Undefined):
                output.value = Value.from_typed(
                    arrNullStruct=self.map_arr(top.arrNullStruct(), self.map_struct))
            if not isinstance(top.objStruct(), Undefined):
                output.value = Value.from_typed(
                    objStruct=self.map_obj(top.objStruct(), self.map_struct))
            if not isinstance(top.objNullStruct(), Undefined):
                output.value = Value.from_typed(
                    objNullStruct=self.map_obj(top.objNullStruct(), self.map_struct))
            if not isinstance(top.union(), Undefined):
                output.value = Value.from_typed(
                    union=self.map_union(top.union()))
            if not isinstance(top.nullUnion(), Undefined):
                output.value = Value.from_typed(
                    nullUnion=self.map_union(top.nullUnion()))
            if not isinstance(top.arrUnion(), Undefined):
                output.value = Value.from_typed(
                    arrUnion=self.map_arr(top.arrUnion(), self.map_union))
            if not isinstance(top.arrNullUnion(), Undefined):
                output.value = Value.from_typed(
                    arrNullUnion=self.map_arr(top.arrNullUnion(), self.map_union))
            if not isinstance(top.objUnion(), Undefined):
                output.value = Value.from_typed(
                    objUnion=self.map_obj(top.objUnion(), self.map_union))
            if not isinstance(top.objNullUnion(), Undefined):
                output.value = Value.from_typed(
                    objNullUnion=self.map_obj(top.objNullUnion(), self.map_union))
            if not isinstance(top.fn(), Undefined):
                output.value = Value.from_typed(fn=self.map_fn(top.fn()))
            if not isinstance(top.nullFn(), Undefined):
                output.value = Value.from_typed(
                    nullFn=self.map_fn(top.nullFn()))
            if not isinstance(top.arrFn(), Undefined):
                output.value = Value.from_typed(
                    arrFn=self.map_arr(top.arrFn(), self.map_fn))
            if not isinstance(top.arrNullFn(), Undefined):
                output.value = Value.from_typed(
                    arrNullFn=self.map_arr(top.arrNullFn(), self.map_fn))
            if not isinstance(top.objFn(), Undefined):
                output.value = Value.from_typed(
                    objFn=self.map_obj(top.objFn(), self.map_fn))
            if not isinstance(top.objNullFn(), Undefined):
                output.value = Value.from_typed(
                    objNullFn=self.map_obj(top.objNullFn(), self.map_fn))

        return {}, output

    def map_struct(self, s: ExStruct) -> ExStruct:
        if s is None:
            return None
        b = ExStruct(
            required=s.required
        )
        if not isinstance(s.optional, Undefined):
            b.optional = s.optional
        if not isinstance(s.optional2, Undefined):
            b.optional2 = s.optional2
        return b

    def map_union(self, u: ExUnion) -> ExUnion:
        if u is None:
            return None
        if isinstance(u, ExUnion__NoMatch_):
            return ExUnion__NoMatch_()
        elif isinstance(u, ExUnion__One):
            return ExUnion__One()
        elif isinstance(u, ExUnion__Two):
            b = ExUnion__Two(
                required=u.required
            )
            if not isinstance(u.optional, Undefined):
                b.optional = u.optional
            return b

    def map_fn(self, f: example__Input_) -> example__Input_:
        if f is None:
            return None
        b = example__Input_(required=f.required)
        if not isinstance(f.optional, Undefined):
            b.optional = f.optional
        return b

    T = TypeVar('T')

    def map_arr(self, l: list[T], mapper: Callable[[T], T]) -> list[T]:
        if l is None:
            return None
        return [mapper(e) for e in l]

    def map_obj(self, m: dict[str, T], mapper: Callable[[T], T]) -> dict[str, T]:
        if m is None:
            return None
        return {k: mapper(v) for k, v in m.items()}

    def get_big_list(self, headers: dict[str, object], input: getBigList__Input_) -> getBigList__Output_:
        raise NotImplementedError("Unimplemented method 'getBigList'")
