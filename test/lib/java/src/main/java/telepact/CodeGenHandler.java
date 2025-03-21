//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

package telepacttest;

import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicReference;
import java.util.HashMap;
import java.util.function.Function;
import java.util.stream.Collectors;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import telepacttest.ExStruct;
import telepacttest.ExUnion;
import telepacttest.ServerHandler_;
import telepacttest.TypedMessage_;
import telepacttest.Value;
import telepacttest.example;
import telepacttest.test;
import telepacttest.example.Input;
import telepacttest.example.Output;

public class CodeGenHandler extends ServerHandler_ {

    @Override
    public TypedMessage_<Output> example(Map<String, Object> headers, Input input) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'example'");
    }

    @Override
    public TypedMessage_<telepacttest.test.Output> test(Map<String, Object> headers, telepacttest.test.Input input) {
        try {
            System.out.println("input: " + new ObjectMapper().writeValueAsString(input.pseudoJson));
        } catch (JsonProcessingException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }

        var value = new AtomicReference<>(new Value.Builder());

        input.value().ifPresent(top -> {
            top.bool().ifPresent(v -> {
                value.set(new Value.Builder().bool(v));
                System.out.println("bool: " + v);
            });
            top.nullBool().ifPresent(v -> {
                value.set(new Value.Builder().nullBool(v));
            });
            top.arrBool().ifPresent(v -> {
                value.set(new Value.Builder().arrBool(v));
            });
            top.arrNullBool().ifPresent(v -> {
                value.set(new Value.Builder().arrNullBool(v));
            });
            top.objBool().ifPresent(v -> {
                value.set(new Value.Builder().objBool(v));
            });
            top.objNullBool().ifPresent(v -> {
                value.set(new Value.Builder().objNullBool(v));
            });
            top.int_().ifPresent(v -> {
                value.set(new Value.Builder().int_(v));
            });
            top.nullInt().ifPresent(v -> {
                value.set(new Value.Builder().nullInt(v));
            });
            top.arrInt().ifPresent(v -> {
                value.set(new Value.Builder().arrInt(v));
            });
            top.arrNullInt().ifPresent(v -> {
                value.set(new Value.Builder().arrNullInt(v));
            });
            top.objInt().ifPresent(v -> {
                value.set(new Value.Builder().objInt(v));
            });
            top.objNullInt().ifPresent(v -> {
                value.set(new Value.Builder().objNullInt(v));
            });
            top.num().ifPresent(v -> {
                value.set(new Value.Builder().num(v));
            });
            top.nullNum().ifPresent(v -> {
                value.set(new Value.Builder().nullNum(v));
            });
            top.arrNum().ifPresent(v -> {
                value.set(new Value.Builder().arrNum(v));
            });
            top.arrNullNum().ifPresent(v -> {
                value.set(new Value.Builder().arrNullNum(v));
            });
            top.objNum().ifPresent(v -> {
                value.set(new Value.Builder().objNum(v));
            });
            top.objNullNum().ifPresent(v -> {
                value.set(new Value.Builder().objNullNum(v));
            });
            top.str().ifPresent(v -> {
                value.set(new Value.Builder().str(v));
            });
            top.nullStr().ifPresent(v -> {
                value.set(new Value.Builder().nullStr(v));
            });
            top.arrStr().ifPresent(v -> {
                value.set(new Value.Builder().arrStr(v));
            });
            top.arrNullStr().ifPresent(v -> {
                value.set(new Value.Builder().arrNullStr(v));
            });
            top.objStr().ifPresent(v -> {
                value.set(new Value.Builder().objStr(v));
            });
            top.objNullStr().ifPresent(v -> {
                value.set(new Value.Builder().objNullStr(v));
            });
            top.arr().ifPresent(v -> {
                value.set(new Value.Builder().arr(v));
            });
            top.nullArr().ifPresent(v -> {
                value.set(new Value.Builder().nullArr(v));
            });
            top.arrArr().ifPresent(v -> {
                value.set(new Value.Builder().arrArr(v));
            });
            top.arrNullArr().ifPresent(v -> {
                value.set(new Value.Builder().arrNullArr(v));
            });
            top.objArr().ifPresent(v -> {
                value.set(new Value.Builder().objArr(v));
            });
            top.objNullArr().ifPresent(v -> {
                value.set(new Value.Builder().objNullArr(v));
            });
            top.obj().ifPresent(v -> {
                value.set(new Value.Builder().obj(v));
            });
            top.nullObj().ifPresent(v -> {
                value.set(new Value.Builder().nullObj(v));
            });
            top.arrObj().ifPresent(v -> {
                value.set(new Value.Builder().arrObj(v));
            });
            top.arrNullObj().ifPresent(v -> {
                value.set(new Value.Builder().arrNullObj(v));
            });
            top.objObj().ifPresent(v -> {
                value.set(new Value.Builder().objObj(v));
            });
            top.objNullObj().ifPresent(v -> {
                value.set(new Value.Builder().objNullObj(v));
            });
            top.any().ifPresent(v -> {
                value.set(new Value.Builder().any(v));
            });
            top.nullAny().ifPresent(v -> {
                value.set(new Value.Builder().nullAny(v));
            });
            top.arrAny().ifPresent(v -> {
                value.set(new Value.Builder().arrAny(v));
            });
            top.arrNullAny().ifPresent(v -> {
                value.set(new Value.Builder().arrNullAny(v));
            });
            top.objAny().ifPresent(v -> {
                value.set(new Value.Builder().objAny(v));
            });
            top.objNullAny().ifPresent(v -> {
                value.set(new Value.Builder().objNullAny(v));
            });

            top.struct().ifPresent(v -> {
                value.set(new Value.Builder().struct(mapStruct(v)));
            });
            top.nullStruct().ifPresent(v -> {
                value.set(new Value.Builder().nullStruct(mapStruct(v)));
            });
            top.arrStruct().ifPresent(v -> {
                value.set(new Value.Builder().arrStruct(mapArr(v, s -> mapStruct(s))));
            });
            top.arrNullStruct().ifPresent(v -> {
                value.set(new Value.Builder().arrNullStruct(mapArr(v, s -> mapStruct(s))));
            });
            top.objStruct().ifPresent(v -> {
                value.set(new Value.Builder().objStruct(mapObj(v, s -> mapStruct(s))));
            });
            top.objNullStruct().ifPresent(v -> {
                value.set(new Value.Builder().objNullStruct(mapObj(v, s -> mapStruct(s))));
            });
            top.union().ifPresent(v -> {
                value.set(new Value.Builder().union(mapUnion(v)));
            });
            top.nullUnion().ifPresent(v -> {
                value.set(new Value.Builder().nullUnion(mapUnion(v)));
            });
            top.arrUnion().ifPresent(v -> {
                value.set(new Value.Builder().arrUnion(mapArr(v, u -> mapUnion(u))));
            });
            top.arrNullUnion().ifPresent(v -> {
                value.set(new Value.Builder().arrNullUnion(mapArr(v, u -> mapUnion(u))));
            });
            top.objUnion().ifPresent(v -> {
                value.set(new Value.Builder().objUnion(mapObj(v, u -> mapUnion(u))));
            });
            top.objNullUnion().ifPresent(v -> {
                value.set(new Value.Builder().objNullUnion(mapObj(v, u -> mapUnion(u))));
            });
            top.fn().ifPresent(v -> {
                value.set(new Value.Builder().fn(mapFn(v)));
            });
            top.nullFn().ifPresent(v -> {
                value.set(new Value.Builder().nullFn(mapFn(v)));
            });
            top.arrFn().ifPresent(v -> {
                value.set(new Value.Builder().arrFn(mapArr(v, f -> mapFn(f))));
            });
            top.arrNullFn().ifPresent(v -> {
                value.set(new Value.Builder().arrNullFn(mapArr(v, f -> mapFn(f))));
            });
            top.objFn().ifPresent(v -> {
                value.set(new Value.Builder().objFn(mapObj(v, f -> mapFn(f))));
            });
            top.objNullFn().ifPresent(v -> {
                value.set(new Value.Builder().objNullFn(mapObj(v, f -> mapFn(f))));
            });
        });

        var ok = new test.Output.Ok_.Builder().value(value.get().build());
        var output = test.Output.from_Ok_(ok.build());

        return new TypedMessage_<test.Output>(new HashMap<>(), output);
    }

    private static ExStruct mapStruct(ExStruct s) {
        if (s == null) {
            return null;
        }
        var b = new ExStruct.Builder();
        b.required(s.required());
        s.optional().ifPresent(b::optional);
        s.optional2().ifPresent(b::optional2);
        return ExStruct.fromTyped(b);
    }

    private static ExUnion mapUnion(ExUnion u) {
        if (u == null) {
            return null;
        }
        var tv = u.getTaggedValue();
        return switch (tv) {
            case ExUnion.Untyped_ v -> new ExUnion(Map.of(v.tag, v.value));
            case ExUnion.One v -> ExUnion.from_One(new ExUnion.One.Builder().build());
            case ExUnion.Two v -> {
                var b = new ExUnion.Two.Builder();
                b.required(v.required());
                v.optional().ifPresent(b::optional);
                yield ExUnion.from_Two(b.build());
            }
            default -> throw new IllegalArgumentException("Unexpected value: " + u);
        };
    }

    private static example.Input mapFn(example.Input f) {
        if (f == null) {
            return null;
        }
        var b = new example.Input.Builder();
        f.optional().ifPresent(b::optional);
        b.required(f.required());
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
    public TypedMessage_<telepacttest.getBigList.Output> getBigList(Map<String, Object> headers,
            telepacttest.getBigList.Input input) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'getBigList'");
    }

}
