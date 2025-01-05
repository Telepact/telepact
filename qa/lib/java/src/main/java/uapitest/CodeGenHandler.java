package uapitest;

import java.util.List;
import java.util.Map;
import java.util.HashMap;
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

        try {
            System.out.println("input: " + new ObjectMapper().writeValueAsString(input.toPseudoJson()));
        } catch (JsonProcessingException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }

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
        });

        return outputBuilder.build();
    }

    private static ExStruct mapStruct(ExStruct s) {
        if (s == null) {
            return null;
        }
        var b = new ExStruct.Builder();
        b.required(s.required);
        s.optional.ifPresent(b::optional);
        s.optional2.ifPresent(b::optional2);
        return b.build();
    }

    private static ExUnion mapUnion(ExUnion u) {
        if (u == null) {
            return null;
        }
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
        if (f == null) {
            return null;
        }
        var b = new example.Input.Builder();
        f.optional.ifPresent(b::optional);
        b.required(f.required);
        return b.build();
    }

    private static <T> List<T> mapArr(List<T> l, Function<T, T> mapper) {
        if (l == null) {
            return null;
        }
        return l.stream().map(e -> mapper.apply(e)).toList();
    }

    private static <T> Map<String, T> mapObj(Map<String, T> m, Function<T, T> mapper) {
        if (m == null) {
            return null;
        }
        return m.entrySet().stream().collect(() -> {
            Map<String, T> r = new HashMap<>();
            return r;
        }, (m2, e) -> m2.put(e.getKey(), mapper.apply(e.getValue())), Map::putAll);
    }

    @Override
    public uapitest.getBigList.Output getBigList(Map<String, Object> headers, uapitest.getBigList.Input input) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'getBigList'");
    }

}
