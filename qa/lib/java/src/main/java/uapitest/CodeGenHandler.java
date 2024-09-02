package uapitest;

import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import uapitest.ServerHandler_;
import uapitest.example.Input;
import uapitest.example.Output;

public class CodeGenHandler extends ServerHandler_ {

    @Override
    public Output example(Map<String, Object> headers, Input input) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'example'");
    }

    @Override
    public uapitest.test.Output test(Map<String, Object> headers, uapitest.test.Input input) {
        var outputBuilder = new uapitest.test.Output.Ok_.Builder();

        input.value.ifPresent(top -> {
            top.bool.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().bool(v).build());
            });
            top.nullBool.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().nullBool(v).build());
            });
            top.arrBool.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrBool(v).build());
            });
            top.arrNullBool.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrNullBool(v).build());
            });
            top.objBool.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().objBool(v).build());
            });
            top.objNullBool.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().objNullBool(v).build());
            });
            top.pStrBool.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pStrBool(mapPStr(v)).build());
            });
            top.pStrNullBool.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pStrNullBool(mapPStr(v)).build());
            });
            top.pUnionBool.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pUnionBool(mapPUnion(v)).build());
            });
            top.pUnionNullBool.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pUnionNullBool(mapPUnion(v)).build());
            });
            top.arrPStrBool.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrPStrBool(mapArrPStr(v)).build());
            });
            top.arrP2StrBool.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrP2StrBool(mapArrP2Str(v)).build());
            });
            top.int_.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().int_(v).build());
            });
            top.nullInt.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().nullInt(v).build());
            });
            top.arrInt.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrInt(v).build());
            });
            top.arrNullInt.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrNullInt(v).build());
            });
            top.objInt.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().objInt(v).build());
            });
            top.objNullInt.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().objNullInt(v).build());
            });
            top.pStrInt.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pStrInt(mapPStr(v)).build());
            });
            top.pStrNullInt.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pStrNullInt(mapPStr(v)).build());
            });
            top.pUnionInt.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pUnionInt(mapPUnion(v)).build());
            });
            top.pUnionNullInt.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pUnionNullInt(mapPUnion(v)).build());
            });
            top.arrPStrInt.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrPStrInt(mapArrPStr(v)).build());
            });
            top.arrP2StrInt.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrP2StrInt(mapArrP2Str(v)).build());
            });
            top.num.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().num(v).build());
            });
            top.nullNum.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().nullNum(v).build());
            });
            top.arrNum.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrNum(v).build());
            });
            top.arrNullNum.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrNullNum(v).build());
            });
            top.objNum.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().objNum(v).build());
            });
            top.objNullNum.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().objNullNum(v).build());
            });
            top.pStrNum.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pStrNum(mapPStr(v)).build());
            });
            top.pStrNullNum.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pStrNullNum(mapPStr(v)).build());
            });
            top.pUnionNum.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pUnionNum(mapPUnion(v)).build());
            });
            top.pUnionNullNum.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pUnionNullNum(mapPUnion(v)).build());
            });
            top.arrPStrNum.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrPStrNum(mapArrPStr(v)).build());
            });
            top.arrP2StrNum.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrP2StrNum(mapArrP2Str(v)).build());
            });
            top.str.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().str(v).build());
            });
            top.nullStr.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().nullStr(v).build());
            });
            top.arrStr.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrStr(v).build());
            });
            top.arrNullStr.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrNullStr(v).build());
            });
            top.objStr.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().objStr(v).build());
            });
            top.objNullStr.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().objNullStr(v).build());
            });
            top.pStrStr.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pStrStr(mapPStr(v)).build());
            });
            top.pStrNullStr.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pStrNullStr(mapPStr(v)).build());
            });
            top.pUnionStr.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pUnionStr(mapPUnion(v)).build());
            });
            top.pUnionNullStr.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pUnionNullStr(mapPUnion(v)).build());
            });
            top.arrPStrStr.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrPStrStr(mapArrPStr(v)).build());
            });
            top.arrP2StrStr.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrP2StrStr(mapArrP2Str(v)).build());
            });
            top.arr.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arr(v).build());
            });
            top.nullArr.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().nullArr(v).build());
            });
            top.arrArr.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrArr(v).build());
            });
            top.arrNullArr.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrNullArr(v).build());
            });
            top.objArr.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().objArr(v).build());
            });
            top.objNullArr.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().objNullArr(v).build());
            });
            top.pStrArr.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pStrArr(mapPStr(v)).build());
            });
            top.pStrNullArr.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pStrNullArr(mapPStr(v)).build());
            });
            top.pUnionArr.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pUnionArr(mapPUnion(v)).build());
            });
            top.pUnionNullArr.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pUnionNullArr(mapPUnion(v)).build());
            });
            top.arrPStrArr.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrPStrArr(mapArrPStr(v)).build());
            });
            top.arrP2StrArr.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrP2StrArr(mapArrP2Str(v)).build());
            });
            top.obj.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().obj(v).build());
            });
            top.nullObj.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().nullObj(v).build());
            });
            top.arrObj.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrObj(v).build());
            });
            top.arrNullObj.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrNullObj(v).build());
            });
            top.objObj.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().objObj(v).build());
            });
            top.objNullObj.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().objNullObj(v).build());
            });
            top.pStrObj.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pStrObj(mapPStr(v)).build());
            });
            top.pStrNullObj.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pStrNullObj(mapPStr(v)).build());
            });
            top.pUnionObj.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pUnionObj(mapPUnion(v)).build());
            });
            top.pUnionNullObj.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pUnionNullObj(mapPUnion(v)).build());
            });
            top.arrPStrObj.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrPStrObj(mapArrPStr(v)).build());
            });
            top.arrP2StrObj.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrP2StrObj(mapArrP2Str(v)).build());
            });
            top.any.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().any(v).build());
            });
            top.nullAny.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().nullAny(v).build());
            });
            top.arrAny.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrAny(v).build());
            });
            top.arrNullAny.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrNullAny(v).build());
            });
            top.objAny.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().objAny(v).build());
            });
            top.objNullAny.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().objNullAny(v).build());
            });
            top.pStrAny.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pStrAny(mapPStr(v)).build());
            });
            top.pStrNullAny.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pStrNullAny(mapPStr(v)).build());
            });
            top.pUnionAny.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pUnionAny(mapPUnion(v)).build());
            });
            top.pUnionNullAny.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pUnionNullAny(mapPUnion(v)).build());
            });
            top.arrPStrAny.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrPStrAny(mapArrPStr(v)).build());
            });
            top.arrP2StrAny.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrP2StrAny(mapArrP2Str(v)).build());
            });

            top.struct.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().struct(mapStruct(v)).build());
            });
            top.nullStruct.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().nullStruct(mapStruct(v)).build());
            });
            top.arrStruct.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrStruct(mapArr(v, s -> mapStruct(s))).build());
            });
            top.arrNullStruct.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrNullStruct(mapArr(v, s -> mapStruct(s))).build());
            });
            top.objStruct.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().objStruct(mapObj(v, s -> mapStruct(s))).build());
            });
            top.objNullStruct.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().objNullStruct(mapObj(v, s -> mapStruct(s))).build());
            });
            top.pStrStruct.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pStrStruct(mapPStr(v, s -> mapStruct(s))).build());
            });
            top.pStrNullStruct.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pStrNullStruct(mapPStr(v, s -> mapStruct(s))).build());
            });
            top.pUnionStruct.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pUnionStruct(mapPUnion(v, s -> mapStruct(s))).build());
            });
            top.pUnionNullStruct.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pUnionNullStruct(mapPUnion(v, s -> mapStruct(s))).build());
            });
            top.arrPStrStruct.ifPresent(v -> {
                outputBuilder.value(
                        new Value.Builder().arrPStrStruct(mapArr(v, p -> mapPStr(p, s -> mapStruct(s)))).build());
            });
            top.arrP2StrStruct.ifPresent(v -> {
                outputBuilder.value(
                        new Value.Builder().arrP2StrStruct(mapArr(v, p2 -> mapP2Str(p2, s -> mapStruct(s)))).build());
            });
            top.union.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().union(mapUnion(v)).build());
            });
            top.nullUnion.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().nullUnion(mapUnion(v)).build());
            });
            top.arrUnion.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrUnion(mapArr(v, u -> mapUnion(u))).build());
            });
            top.arrNullUnion.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrNullUnion(mapArr(v, u -> mapUnion(u))).build());
            });
            top.objUnion.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().objUnion(mapObj(v, u -> mapUnion(u))).build());
            });
            top.objNullUnion.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().objNullUnion(mapObj(v, u -> mapUnion(u))).build());
            });
            top.pStrUnion.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pStrUnion(mapPStr(v, u -> mapUnion(u))).build());
            });
            top.pStrNullUnion.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pStrNullUnion(mapPStr(v, u -> mapUnion(u))).build());
            });
            top.pUnionUnion.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pUnionUnion(mapPUnion(v, u -> mapUnion(u))).build());
            });
            top.pUnionNullUnion.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pUnionNullUnion(mapPUnion(v, u -> mapUnion(u))).build());
            });
            top.arrPStrUnion.ifPresent(v -> {
                outputBuilder
                        .value(new Value.Builder().arrPStrUnion(mapArr(v, p -> mapPStr(p, u -> mapUnion(u)))).build());
            });
            top.arrP2StrUnion.ifPresent(v -> {
                outputBuilder.value(
                        new Value.Builder().arrP2StrUnion(mapArr(v, p2 -> mapP2Str(p2, u -> mapUnion(u)))).build());
            });
            top.fn.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().fn(mapFn(v)).build());
            });
            top.nullFn.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().nullFn(mapFn(v)).build());
            });
            top.arrFn.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrFn(mapArr(v, f -> mapFn(f))).build());
            });
            top.arrNullFn.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrNullFn(mapArr(v, f -> mapFn(f))).build());
            });
            top.objFn.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().objFn(mapObj(v, f -> mapFn(f))).build());
            });
            top.objNullFn.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().objNullFn(mapObj(v, f -> mapFn(f))).build());
            });
            top.pStrFn.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pStrFn(mapPStr(v, f -> mapFn(f))).build());
            });
            top.pStrNullFn.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pStrNullFn(mapPStr(v, f -> mapFn(f))).build());
            });
            top.pUnionFn.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pUnionFn(mapPUnion(v, f -> mapFn(f))).build());
            });
            top.pUnionNullFn.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pUnionNullFn(mapPUnion(v, f -> mapFn(f))).build());
            });
            top.arrPStrFn.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrPStrFn(mapArr(v, p -> mapPStr(p, f -> mapFn(f)))).build());
            });
            top.arrP2StrFn.ifPresent(v -> {
                outputBuilder
                        .value(new Value.Builder().arrP2StrFn(mapArr(v, p2 -> mapP2Str(p2, f -> mapFn(f)))).build());
            });
            top.p2Str.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().p2Str(mapP2Str(v)).build());
            });
            top.nullP2Str.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().nullP2Str(mapP2Str(v)).build());
            });
            top.arrP2Str.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrP2Str(mapArr(v, p -> mapP2Str(p))).build());
            });
            top.arrNullP2Str.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrNullP2Str(mapArr(v, p -> mapP2Str(p))).build());
            });
            top.objP2Str.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().objP2Str(mapObj(v, p -> mapP2Str(p))).build());
            });
            top.objNullP2Str.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().objNullP2Str(mapObj(v, p -> mapP2Str(p))).build());
            });
            top.pStrP2Str.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pStrP2Str(mapPStr(v, p -> mapP2Str(p))).build());
            });
            top.pStrNullP2Str.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pStrNullP2Str(mapPStr(v, p -> mapP2Str(p))).build());
            });
            top.pUnionP2Str.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pUnionP2Str(mapPUnion(v, p -> mapP2Str(p))).build());
            });
            top.pUnionNullP2Str.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pUnionNullP2Str(mapPUnion(v, p -> mapP2Str(p))).build());
            });
            top.arrPStrP2Str.ifPresent(v -> {
                outputBuilder.value(
                        new Value.Builder().arrPStrP2Str(mapArr(v, p -> mapPStr(p, p2 -> mapP2Str(p2)))).build());
            });
            top.arrP2StrP2Str.ifPresent(v -> {
                outputBuilder.value(
                        new Value.Builder().arrP2StrP2Str(mapArr(v, p2 -> mapP2Str(p2, p22 -> mapP2Str(p22)))).build());
            });
            top.p2Union.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().p2Union(mapP2Union(v)).build());
            });
            top.nullP2Union.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().nullP2Union(mapP2Union(v)).build());
            });
            top.arrP2Union.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrP2Union(mapArr(v, p -> mapP2Union(p))).build());
            });

            top.arrNullP2Union.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().arrNullP2Union(mapArr(v, p -> mapP2Union(p))).build());
            });
            top.objP2Union.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().objP2Union(mapObj(v, p -> mapP2Union(p))).build());
            });
            top.objNullP2Union.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().objNullP2Union(mapObj(v, p -> mapP2Union(p))).build());
            });
            top.pStrP2Union.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pStrP2Union(mapPStr(v, p -> mapP2Union(p))).build());
            });
            top.pStrNullP2Union.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pStrNullP2Union(mapPStr(v, p -> mapP2Union(p))).build());
            });
            top.pUnionP2Union.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pUnionP2Union(mapPUnion(v, p -> mapP2Union(p))).build());
            });
            top.pUnionNullP2Union.ifPresent(v -> {
                outputBuilder.value(new Value.Builder().pUnionNullP2Union(mapPUnion(v, p -> mapP2Union(p))).build());
            });
            top.arrPStrP2Union.ifPresent(v -> {
                outputBuilder.value(
                        new Value.Builder().arrPStrP2Union(mapArr(v, p -> mapPStr(p, p2 -> mapP2Union(p2)))).build());
            });
            top.arrP2StrP2Union.ifPresent(v -> {
                outputBuilder.value(new Value.Builder()
                        .arrP2StrP2Union(mapArr(v, p2 -> mapP2Str(p2, p22 -> mapP2Union(p22)))).build());
            });
            top.pdStr.ifPresent(v -> {
                PdStr<PStr<Boolean>> pdStr = new PdStr.Builder<PStr<Boolean>>().dwrap(v.dwrap).build();
                outputBuilder.value(new Value.Builder().pdStr(pdStr).build());
            });

        });

        return outputBuilder.build();
    }

    private static <T> PStr<T> mapPStr(PStr<T> s) {
        return new PStr.Builder<T>().wrap(s.wrap).build();
    }

    private static <T> PStr<T> mapPStr(PStr<T> s, Function<T, T> mapper) {
        return new PStr.Builder<T>().wrap(mapper.apply(s.wrap)).build();
    }

    private static <T, U> P2Str<T, U> mapP2Str(P2Str<T, U> s) {
        return new P2Str.Builder<T, U>().wrap(s.wrap).nest(s.nest).build();
    }

    private static <T, U> P2Str<T, U> mapP2Str(P2Str<T, U> s, Function<U, U> mapper) {
        return new P2Str.Builder<T, U>().wrap(s.wrap).nest(s.nest).build();
    }

    private static <T> PUnion<T> mapPUnion(PUnion<T> u) {
        return switch (u) {
            case PUnion.NoMatch_<T> v -> new PUnion.NoMatch_<T>(new PUnion.NoMatch_.Builder<>());
            case PUnion.One<T> v -> new PUnion.One.Builder<T>().build();
            case PUnion.Two<T> v -> new PUnion.Two.Builder<T>().ewrap(v.ewrap).build();
        };
    }

    private static <T> PUnion<T> mapPUnion(PUnion<T> u, Function<T, T> mapper) {
        return switch (u) {
            case PUnion.NoMatch_<T> v -> new PUnion.NoMatch_<T>(new PUnion.NoMatch_.Builder<>());
            case PUnion.One<T> v -> new PUnion.One.Builder<T>().build();
            case PUnion.Two<T> v -> new PUnion.Two.Builder<T>().ewrap(mapper.apply(v.ewrap)).build();
        };
    }

    private static <T> List<PStr<T>> mapArrPStr(List<PStr<T>> l) {
        return l.stream().map(v -> mapPStr(v)).toList();
    }

    private static <T> List<P2Str<Boolean, T>> mapArrP2Str(List<P2Str<Boolean, T>> l) {
        return l.stream().map(v -> mapP2Str(v)).toList();
    }

    private static ExStruct mapStruct(ExStruct s) {
        var b = new ExStruct.Builder();
        b.required(s.required);
        s.optional.ifPresent(b::optional);
        s.optional2.ifPresent(b::optional2);
        return b.build();
    }

    private static ExUnion mapUnion(ExUnion u) {
        return switch (u) {
            case ExUnion.NoMatch_ v -> new ExUnion.NoMatch_(new ExUnion.NoMatch_.Builder());
            case ExUnion.One v -> new ExUnion.One.Builder().build();
            case ExUnion.Two v -> {
                var b = new ExUnion.Two.Builder();
                b.required(v.required);
                v.optional.ifPresent(b::optional);
                yield b.build();
            }
        };
    }

    private static example.Input mapFn(example.Input f) {
        var b = new example.Input.Builder();
        f.optional.ifPresent(b::optional);
        b.required(f.required);
        return b.build();
    }

    private static <T> List<T> mapArr(List<T> l, Function<T, T> mapper) {
        return l.stream().map(e -> mapper.apply(e)).toList();
    }

    private static <T> Map<String, T> mapObj(Map<String, T> m, Function<T, T> mapper) {
        return m.entrySet().stream().collect(Collectors.toMap(Map.Entry::getKey, e -> mapper.apply(e.getValue())));
    }

    private static <T, U> P2Union<T, U> mapP2Union(P2Union<T, U> u) {
        return switch (u) {
            case P2Union.NoMatch_<T, U> v -> new P2Union.NoMatch_.Builder<T, U>().build();
            case P2Union.One<T, U> v -> new P2Union.One.Builder<T, U>().build();
            case P2Union.Two<T, U> v -> new P2Union.Two.Builder<T, U>().ewrap(v.ewrap).enest(v.enest).build();
        };
    }

    @Override
    public uapitest.getBigList.Output getBigList(Map<String, Object> headers, uapitest.getBigList.Input input) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'getBigList'");
    }

}
