package uapitest;

import java.util.AbstractMap;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
    
/**
 * A struct value demonstrating all common type permutations. 
 */
public class Value {
    public final Map<String, Object> pseudoJson;

    public Value(Map<String, Object> pseudoJson) {
        this.pseudoJson = pseudoJson;
    }

    public static Value fromTyped(Builder b) {
        var map = new HashMap<String, Object>();
        b.bool.ifPresent(f -> {
            map.put("bool!", f);
        });
        b.nullBool.ifPresent(f -> {
            map.put("nullBool!", f);
        });
        b.arrBool.ifPresent(f -> {
            map.put("arrBool!", Utility_.let(f, d0 -> d0 == null ? null : d0.stream().map(e0 -> e0).toList()));
        });
        b.arrNullBool.ifPresent(f -> {
            map.put("arrNullBool!", Utility_.let(f, d0 -> d0 == null ? null : d0.stream().map(e0 -> e0).toList()));
        });
        b.objBool.ifPresent(f -> {
            map.put("objBool!", Utility_.let(f, d0 -> d0 == null ? null : d0.entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), e0.getValue())).collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), Map::putAll)));
        });
        b.objNullBool.ifPresent(f -> {
            map.put("objNullBool!", Utility_.let(f, d0 -> d0 == null ? null : d0.entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), e0.getValue())).collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), Map::putAll)));
        });
        b.int_.ifPresent(f -> {
            map.put("int!", f);
        });
        b.nullInt.ifPresent(f -> {
            map.put("nullInt!", f);
        });
        b.arrInt.ifPresent(f -> {
            map.put("arrInt!", Utility_.let(f, d0 -> d0 == null ? null : d0.stream().map(e0 -> e0).toList()));
        });
        b.arrNullInt.ifPresent(f -> {
            map.put("arrNullInt!", Utility_.let(f, d0 -> d0 == null ? null : d0.stream().map(e0 -> e0).toList()));
        });
        b.objInt.ifPresent(f -> {
            map.put("objInt!", Utility_.let(f, d0 -> d0 == null ? null : d0.entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), e0.getValue())).collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), Map::putAll)));
        });
        b.objNullInt.ifPresent(f -> {
            map.put("objNullInt!", Utility_.let(f, d0 -> d0 == null ? null : d0.entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), e0.getValue())).collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), Map::putAll)));
        });
        b.num.ifPresent(f -> {
            map.put("num!", f);
        });
        b.nullNum.ifPresent(f -> {
            map.put("nullNum!", f);
        });
        b.arrNum.ifPresent(f -> {
            map.put("arrNum!", Utility_.let(f, d0 -> d0 == null ? null : d0.stream().map(e0 -> e0).toList()));
        });
        b.arrNullNum.ifPresent(f -> {
            map.put("arrNullNum!", Utility_.let(f, d0 -> d0 == null ? null : d0.stream().map(e0 -> e0).toList()));
        });
        b.objNum.ifPresent(f -> {
            map.put("objNum!", Utility_.let(f, d0 -> d0 == null ? null : d0.entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), e0.getValue())).collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), Map::putAll)));
        });
        b.objNullNum.ifPresent(f -> {
            map.put("objNullNum!", Utility_.let(f, d0 -> d0 == null ? null : d0.entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), e0.getValue())).collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), Map::putAll)));
        });
        b.str.ifPresent(f -> {
            map.put("str!", f);
        });
        b.nullStr.ifPresent(f -> {
            map.put("nullStr!", f);
        });
        b.arrStr.ifPresent(f -> {
            map.put("arrStr!", Utility_.let(f, d0 -> d0 == null ? null : d0.stream().map(e0 -> e0).toList()));
        });
        b.arrNullStr.ifPresent(f -> {
            map.put("arrNullStr!", Utility_.let(f, d0 -> d0 == null ? null : d0.stream().map(e0 -> e0).toList()));
        });
        b.objStr.ifPresent(f -> {
            map.put("objStr!", Utility_.let(f, d0 -> d0 == null ? null : d0.entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), e0.getValue())).collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), Map::putAll)));
        });
        b.objNullStr.ifPresent(f -> {
            map.put("objNullStr!", Utility_.let(f, d0 -> d0 == null ? null : d0.entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), e0.getValue())).collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), Map::putAll)));
        });
        b.arr.ifPresent(f -> {
            map.put("arr!", Utility_.let(f, d0 -> d0 == null ? null : d0.stream().map(e0 -> e0).toList()));
        });
        b.nullArr.ifPresent(f -> {
            map.put("nullArr!", Utility_.let(f, d0 -> d0 == null ? null : d0.stream().map(e0 -> e0).toList()));
        });
        b.arrArr.ifPresent(f -> {
            map.put("arrArr!", Utility_.let(f, d0 -> d0 == null ? null : d0.stream().map(e0 -> Utility_.let(e0, d1 -> d1 == null ? null : d1.stream().map(e1 -> e1).toList())).toList()));
        });
        b.arrNullArr.ifPresent(f -> {
            map.put("arrNullArr!", Utility_.let(f, d0 -> d0 == null ? null : d0.stream().map(e0 -> Utility_.let(e0, d1 -> d1 == null ? null : d1.stream().map(e1 -> e1).toList())).toList()));
        });
        b.objArr.ifPresent(f -> {
            map.put("objArr!", Utility_.let(f, d0 -> d0 == null ? null : d0.entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), Utility_.let(e0.getValue(), d1 -> d1 == null ? null : d1.stream().map(e1 -> e1).toList()))).collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), Map::putAll)));
        });
        b.objNullArr.ifPresent(f -> {
            map.put("objNullArr!", Utility_.let(f, d0 -> d0 == null ? null : d0.entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), Utility_.let(e0.getValue(), d1 -> d1 == null ? null : d1.stream().map(e1 -> e1).toList()))).collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), Map::putAll)));
        });
        b.obj.ifPresent(f -> {
            map.put("obj!", Utility_.let(f, d0 -> d0 == null ? null : d0.entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), e0.getValue())).collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), Map::putAll)));
        });
        b.nullObj.ifPresent(f -> {
            map.put("nullObj!", Utility_.let(f, d0 -> d0 == null ? null : d0.entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), e0.getValue())).collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), Map::putAll)));
        });
        b.arrObj.ifPresent(f -> {
            map.put("arrObj!", Utility_.let(f, d0 -> d0 == null ? null : d0.stream().map(e0 -> Utility_.let(e0, d1 -> d1 == null ? null : d1.entrySet().stream().map(e1 -> new AbstractMap.SimpleEntry<>(e1.getKey(), e1.getValue())).collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), Map::putAll))).toList()));
        });
        b.arrNullObj.ifPresent(f -> {
            map.put("arrNullObj!", Utility_.let(f, d0 -> d0 == null ? null : d0.stream().map(e0 -> Utility_.let(e0, d1 -> d1 == null ? null : d1.entrySet().stream().map(e1 -> new AbstractMap.SimpleEntry<>(e1.getKey(), e1.getValue())).collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), Map::putAll))).toList()));
        });
        b.objObj.ifPresent(f -> {
            map.put("objObj!", Utility_.let(f, d0 -> d0 == null ? null : d0.entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), Utility_.let(e0.getValue(), d1 -> d1 == null ? null : d1.entrySet().stream().map(e1 -> new AbstractMap.SimpleEntry<>(e1.getKey(), e1.getValue())).collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), Map::putAll)))).collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), Map::putAll)));
        });
        b.objNullObj.ifPresent(f -> {
            map.put("objNullObj!", Utility_.let(f, d0 -> d0 == null ? null : d0.entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), Utility_.let(e0.getValue(), d1 -> d1 == null ? null : d1.entrySet().stream().map(e1 -> new AbstractMap.SimpleEntry<>(e1.getKey(), e1.getValue())).collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), Map::putAll)))).collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), Map::putAll)));
        });
        b.any.ifPresent(f -> {
            map.put("any!", f);
        });
        b.nullAny.ifPresent(f -> {
            map.put("nullAny!", f);
        });
        b.arrAny.ifPresent(f -> {
            map.put("arrAny!", Utility_.let(f, d0 -> d0 == null ? null : d0.stream().map(e0 -> e0).toList()));
        });
        b.arrNullAny.ifPresent(f -> {
            map.put("arrNullAny!", Utility_.let(f, d0 -> d0 == null ? null : d0.stream().map(e0 -> e0).toList()));
        });
        b.objAny.ifPresent(f -> {
            map.put("objAny!", Utility_.let(f, d0 -> d0 == null ? null : d0.entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), e0.getValue())).collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), Map::putAll)));
        });
        b.objNullAny.ifPresent(f -> {
            map.put("objNullAny!", Utility_.let(f, d0 -> d0 == null ? null : d0.entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), e0.getValue())).collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), Map::putAll)));
        });
        b.struct.ifPresent(f -> {
            map.put("struct!", Utility_.let(f, d0 -> d0 == null ? null : d0.pseudoJson));
        });
        b.nullStruct.ifPresent(f -> {
            map.put("nullStruct!", Utility_.let(f, d0 -> d0 == null ? null : d0.pseudoJson));
        });
        b.arrStruct.ifPresent(f -> {
            map.put("arrStruct!", Utility_.let(f, d0 -> d0 == null ? null : d0.stream().map(e0 -> Utility_.let(e0, d1 -> d1 == null ? null : d1.pseudoJson)).toList()));
        });
        b.arrNullStruct.ifPresent(f -> {
            map.put("arrNullStruct!", Utility_.let(f, d0 -> d0 == null ? null : d0.stream().map(e0 -> Utility_.let(e0, d1 -> d1 == null ? null : d1.pseudoJson)).toList()));
        });
        b.objStruct.ifPresent(f -> {
            map.put("objStruct!", Utility_.let(f, d0 -> d0 == null ? null : d0.entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), Utility_.let(e0.getValue(), d1 -> d1 == null ? null : d1.pseudoJson))).collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), Map::putAll)));
        });
        b.objNullStruct.ifPresent(f -> {
            map.put("objNullStruct!", Utility_.let(f, d0 -> d0 == null ? null : d0.entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), Utility_.let(e0.getValue(), d1 -> d1 == null ? null : d1.pseudoJson))).collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), Map::putAll)));
        });
        b.union.ifPresent(f -> {
            map.put("union!", Utility_.let(f, d0 -> d0 == null ? null : d0.pseudoJson));
        });
        b.nullUnion.ifPresent(f -> {
            map.put("nullUnion!", Utility_.let(f, d0 -> d0 == null ? null : d0.pseudoJson));
        });
        b.arrUnion.ifPresent(f -> {
            map.put("arrUnion!", Utility_.let(f, d0 -> d0 == null ? null : d0.stream().map(e0 -> Utility_.let(e0, d1 -> d1 == null ? null : d1.pseudoJson)).toList()));
        });
        b.arrNullUnion.ifPresent(f -> {
            map.put("arrNullUnion!", Utility_.let(f, d0 -> d0 == null ? null : d0.stream().map(e0 -> Utility_.let(e0, d1 -> d1 == null ? null : d1.pseudoJson)).toList()));
        });
        b.objUnion.ifPresent(f -> {
            map.put("objUnion!", Utility_.let(f, d0 -> d0 == null ? null : d0.entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), Utility_.let(e0.getValue(), d1 -> d1 == null ? null : d1.pseudoJson))).collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), Map::putAll)));
        });
        b.objNullUnion.ifPresent(f -> {
            map.put("objNullUnion!", Utility_.let(f, d0 -> d0 == null ? null : d0.entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), Utility_.let(e0.getValue(), d1 -> d1 == null ? null : d1.pseudoJson))).collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), Map::putAll)));
        });
        b.fn.ifPresent(f -> {
            map.put("fn!", Utility_.let(f, d0 -> d0 == null ? null : d0.pseudoJson));
        });
        b.nullFn.ifPresent(f -> {
            map.put("nullFn!", Utility_.let(f, d0 -> d0 == null ? null : d0.pseudoJson));
        });
        b.arrFn.ifPresent(f -> {
            map.put("arrFn!", Utility_.let(f, d0 -> d0 == null ? null : d0.stream().map(e0 -> Utility_.let(e0, d1 -> d1 == null ? null : d1.pseudoJson)).toList()));
        });
        b.arrNullFn.ifPresent(f -> {
            map.put("arrNullFn!", Utility_.let(f, d0 -> d0 == null ? null : d0.stream().map(e0 -> Utility_.let(e0, d1 -> d1 == null ? null : d1.pseudoJson)).toList()));
        });
        b.objFn.ifPresent(f -> {
            map.put("objFn!", Utility_.let(f, d0 -> d0 == null ? null : d0.entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), Utility_.let(e0.getValue(), d1 -> d1 == null ? null : d1.pseudoJson))).collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), Map::putAll)));
        });
        b.objNullFn.ifPresent(f -> {
            map.put("objNullFn!", Utility_.let(f, d0 -> d0 == null ? null : d0.entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), Utility_.let(e0.getValue(), d1 -> d1 == null ? null : d1.pseudoJson))).collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), Map::putAll)));
        });
        return new Value(map);
    }

    
    public Optional_<Boolean> bool() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("bool!") ? new Optional_<Boolean>((Boolean) ((Map<String, Object>) this.pseudoJson).get("bool!")) : new Optional_<>();
        
    };
    
    public Optional_<Boolean> nullBool() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("nullBool!") ? new Optional_<Boolean>((Boolean) ((Map<String, Object>) this.pseudoJson).get("nullBool!")) : new Optional_<>();
        
    };
    
    public Optional_<List<Boolean>> arrBool() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("arrBool!") ? new Optional_<List<Boolean>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("arrBool!"), d0 -> d0 == null ? null : ((List<?>) d0).stream().map(e0 -> (Boolean) e0).toList())) : new Optional_<>();
        
    };
    
    public Optional_<List<Boolean>> arrNullBool() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("arrNullBool!") ? new Optional_<List<Boolean>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("arrNullBool!"), d0 -> d0 == null ? null : ((List<?>) d0).stream().map(e0 -> (Boolean) e0).toList())) : new Optional_<>();
        
    };
    
    public Optional_<Map<String, Boolean>> objBool() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("objBool!") ? new Optional_<Map<String, Boolean>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("objBool!"), d0 -> d0 == null ? null : ((Map<String, ?>) d0).entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), (Boolean) e0.getValue())).collect(() -> { Map<String, Boolean> m = new HashMap<>(); return m; }, (m, e) -> m.put(e.getKey(), (Boolean) e.getValue()), Map::putAll))) : new Optional_<>();
        
    };
    
    public Optional_<Map<String, Boolean>> objNullBool() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("objNullBool!") ? new Optional_<Map<String, Boolean>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("objNullBool!"), d0 -> d0 == null ? null : ((Map<String, ?>) d0).entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), (Boolean) e0.getValue())).collect(() -> { Map<String, Boolean> m = new HashMap<>(); return m; }, (m, e) -> m.put(e.getKey(), (Boolean) e.getValue()), Map::putAll))) : new Optional_<>();
        
    };
    
    public Optional_<Long> int_() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("int!") ? new Optional_<Long>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("int!"), d0 -> d0 == null ? null : d0 instanceof Integer ? ((Integer) d0).longValue() : (Long) d0)) : new Optional_<>();
        
    };
    
    public Optional_<Long> nullInt() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("nullInt!") ? new Optional_<Long>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("nullInt!"), d0 -> d0 == null ? null : d0 instanceof Integer ? ((Integer) d0).longValue() : (Long) d0)) : new Optional_<>();
        
    };
    
    public Optional_<List<Long>> arrInt() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("arrInt!") ? new Optional_<List<Long>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("arrInt!"), d0 -> d0 == null ? null : ((List<?>) d0).stream().map(e0 -> Utility_.let(e0, d1 -> d1 == null ? null : d1 instanceof Integer ? ((Integer) d1).longValue() : (Long) d1)).toList())) : new Optional_<>();
        
    };
    
    public Optional_<List<Long>> arrNullInt() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("arrNullInt!") ? new Optional_<List<Long>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("arrNullInt!"), d0 -> d0 == null ? null : ((List<?>) d0).stream().map(e0 -> Utility_.let(e0, d1 -> d1 == null ? null : d1 instanceof Integer ? ((Integer) d1).longValue() : (Long) d1)).toList())) : new Optional_<>();
        
    };
    
    public Optional_<Map<String, Long>> objInt() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("objInt!") ? new Optional_<Map<String, Long>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("objInt!"), d0 -> d0 == null ? null : ((Map<String, ?>) d0).entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), Utility_.let(e0.getValue(), d1 -> d1 == null ? null : d1 instanceof Integer ? ((Integer) d1).longValue() : (Long) d1))).collect(() -> { Map<String, Long> m = new HashMap<>(); return m; }, (m, e) -> m.put(e.getKey(), (Long) e.getValue()), Map::putAll))) : new Optional_<>();
        
    };
    
    public Optional_<Map<String, Long>> objNullInt() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("objNullInt!") ? new Optional_<Map<String, Long>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("objNullInt!"), d0 -> d0 == null ? null : ((Map<String, ?>) d0).entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), Utility_.let(e0.getValue(), d1 -> d1 == null ? null : d1 instanceof Integer ? ((Integer) d1).longValue() : (Long) d1))).collect(() -> { Map<String, Long> m = new HashMap<>(); return m; }, (m, e) -> m.put(e.getKey(), (Long) e.getValue()), Map::putAll))) : new Optional_<>();
        
    };
    
    public Optional_<Number> num() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("num!") ? new Optional_<Number>((Number) ((Map<String, Object>) this.pseudoJson).get("num!")) : new Optional_<>();
        
    };
    
    public Optional_<Number> nullNum() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("nullNum!") ? new Optional_<Number>((Number) ((Map<String, Object>) this.pseudoJson).get("nullNum!")) : new Optional_<>();
        
    };
    
    public Optional_<List<Number>> arrNum() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("arrNum!") ? new Optional_<List<Number>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("arrNum!"), d0 -> d0 == null ? null : ((List<?>) d0).stream().map(e0 -> (Number) e0).toList())) : new Optional_<>();
        
    };
    
    public Optional_<List<Number>> arrNullNum() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("arrNullNum!") ? new Optional_<List<Number>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("arrNullNum!"), d0 -> d0 == null ? null : ((List<?>) d0).stream().map(e0 -> (Number) e0).toList())) : new Optional_<>();
        
    };
    
    public Optional_<Map<String, Number>> objNum() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("objNum!") ? new Optional_<Map<String, Number>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("objNum!"), d0 -> d0 == null ? null : ((Map<String, ?>) d0).entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), (Number) e0.getValue())).collect(() -> { Map<String, Number> m = new HashMap<>(); return m; }, (m, e) -> m.put(e.getKey(), (Number) e.getValue()), Map::putAll))) : new Optional_<>();
        
    };
    
    public Optional_<Map<String, Number>> objNullNum() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("objNullNum!") ? new Optional_<Map<String, Number>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("objNullNum!"), d0 -> d0 == null ? null : ((Map<String, ?>) d0).entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), (Number) e0.getValue())).collect(() -> { Map<String, Number> m = new HashMap<>(); return m; }, (m, e) -> m.put(e.getKey(), (Number) e.getValue()), Map::putAll))) : new Optional_<>();
        
    };
    
    public Optional_<String> str() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("str!") ? new Optional_<String>((String) ((Map<String, Object>) this.pseudoJson).get("str!")) : new Optional_<>();
        
    };
    
    public Optional_<String> nullStr() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("nullStr!") ? new Optional_<String>((String) ((Map<String, Object>) this.pseudoJson).get("nullStr!")) : new Optional_<>();
        
    };
    
    public Optional_<List<String>> arrStr() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("arrStr!") ? new Optional_<List<String>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("arrStr!"), d0 -> d0 == null ? null : ((List<?>) d0).stream().map(e0 -> (String) e0).toList())) : new Optional_<>();
        
    };
    
    public Optional_<List<String>> arrNullStr() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("arrNullStr!") ? new Optional_<List<String>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("arrNullStr!"), d0 -> d0 == null ? null : ((List<?>) d0).stream().map(e0 -> (String) e0).toList())) : new Optional_<>();
        
    };
    
    public Optional_<Map<String, String>> objStr() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("objStr!") ? new Optional_<Map<String, String>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("objStr!"), d0 -> d0 == null ? null : ((Map<String, ?>) d0).entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), (String) e0.getValue())).collect(() -> { Map<String, String> m = new HashMap<>(); return m; }, (m, e) -> m.put(e.getKey(), (String) e.getValue()), Map::putAll))) : new Optional_<>();
        
    };
    
    public Optional_<Map<String, String>> objNullStr() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("objNullStr!") ? new Optional_<Map<String, String>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("objNullStr!"), d0 -> d0 == null ? null : ((Map<String, ?>) d0).entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), (String) e0.getValue())).collect(() -> { Map<String, String> m = new HashMap<>(); return m; }, (m, e) -> m.put(e.getKey(), (String) e.getValue()), Map::putAll))) : new Optional_<>();
        
    };
    
    public Optional_<List<Object>> arr() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("arr!") ? new Optional_<List<Object>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("arr!"), d0 -> d0 == null ? null : ((List<?>) d0).stream().map(e0 -> (Object) e0).toList())) : new Optional_<>();
        
    };
    
    public Optional_<List<Object>> nullArr() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("nullArr!") ? new Optional_<List<Object>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("nullArr!"), d0 -> d0 == null ? null : ((List<?>) d0).stream().map(e0 -> (Object) e0).toList())) : new Optional_<>();
        
    };
    
    public Optional_<List<List<Object>>> arrArr() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("arrArr!") ? new Optional_<List<List<Object>>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("arrArr!"), d0 -> d0 == null ? null : ((List<?>) d0).stream().map(e0 -> Utility_.let(e0, d1 -> d1 == null ? null : ((List<?>) d1).stream().map(e1 -> (Object) e1).toList())).toList())) : new Optional_<>();
        
    };
    
    public Optional_<List<List<Object>>> arrNullArr() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("arrNullArr!") ? new Optional_<List<List<Object>>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("arrNullArr!"), d0 -> d0 == null ? null : ((List<?>) d0).stream().map(e0 -> Utility_.let(e0, d1 -> d1 == null ? null : ((List<?>) d1).stream().map(e1 -> (Object) e1).toList())).toList())) : new Optional_<>();
        
    };
    
    public Optional_<Map<String, List<Object>>> objArr() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("objArr!") ? new Optional_<Map<String, List<Object>>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("objArr!"), d0 -> d0 == null ? null : ((Map<String, ?>) d0).entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), Utility_.let(e0.getValue(), d1 -> d1 == null ? null : ((List<?>) d1).stream().map(e1 -> (Object) e1).toList()))).collect(() -> { Map<String, List<Object>> m = new HashMap<>(); return m; }, (m, e) -> m.put(e.getKey(), (List<Object>) e.getValue()), Map::putAll))) : new Optional_<>();
        
    };
    
    public Optional_<Map<String, List<Object>>> objNullArr() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("objNullArr!") ? new Optional_<Map<String, List<Object>>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("objNullArr!"), d0 -> d0 == null ? null : ((Map<String, ?>) d0).entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), Utility_.let(e0.getValue(), d1 -> d1 == null ? null : ((List<?>) d1).stream().map(e1 -> (Object) e1).toList()))).collect(() -> { Map<String, List<Object>> m = new HashMap<>(); return m; }, (m, e) -> m.put(e.getKey(), (List<Object>) e.getValue()), Map::putAll))) : new Optional_<>();
        
    };
    
    public Optional_<Map<String, Object>> obj() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("obj!") ? new Optional_<Map<String, Object>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("obj!"), d0 -> d0 == null ? null : ((Map<String, ?>) d0).entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), (Object) e0.getValue())).collect(() -> { Map<String, Object> m = new HashMap<>(); return m; }, (m, e) -> m.put(e.getKey(), (Object) e.getValue()), Map::putAll))) : new Optional_<>();
        
    };
    
    public Optional_<Map<String, Object>> nullObj() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("nullObj!") ? new Optional_<Map<String, Object>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("nullObj!"), d0 -> d0 == null ? null : ((Map<String, ?>) d0).entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), (Object) e0.getValue())).collect(() -> { Map<String, Object> m = new HashMap<>(); return m; }, (m, e) -> m.put(e.getKey(), (Object) e.getValue()), Map::putAll))) : new Optional_<>();
        
    };
    
    public Optional_<List<Map<String, Object>>> arrObj() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("arrObj!") ? new Optional_<List<Map<String, Object>>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("arrObj!"), d0 -> d0 == null ? null : ((List<?>) d0).stream().map(e0 -> Utility_.let(e0, d1 -> d1 == null ? null : ((Map<String, ?>) d1).entrySet().stream().map(e1 -> new AbstractMap.SimpleEntry<>(e1.getKey(), (Object) e1.getValue())).collect(() -> { Map<String, Object> m = new HashMap<>(); return m; }, (m, e) -> m.put(e.getKey(), (Object) e.getValue()), Map::putAll))).toList())) : new Optional_<>();
        
    };
    
    public Optional_<List<Map<String, Object>>> arrNullObj() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("arrNullObj!") ? new Optional_<List<Map<String, Object>>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("arrNullObj!"), d0 -> d0 == null ? null : ((List<?>) d0).stream().map(e0 -> Utility_.let(e0, d1 -> d1 == null ? null : ((Map<String, ?>) d1).entrySet().stream().map(e1 -> new AbstractMap.SimpleEntry<>(e1.getKey(), (Object) e1.getValue())).collect(() -> { Map<String, Object> m = new HashMap<>(); return m; }, (m, e) -> m.put(e.getKey(), (Object) e.getValue()), Map::putAll))).toList())) : new Optional_<>();
        
    };
    
    public Optional_<Map<String, Map<String, Object>>> objObj() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("objObj!") ? new Optional_<Map<String, Map<String, Object>>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("objObj!"), d0 -> d0 == null ? null : ((Map<String, ?>) d0).entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), Utility_.let(e0.getValue(), d1 -> d1 == null ? null : ((Map<String, ?>) d1).entrySet().stream().map(e1 -> new AbstractMap.SimpleEntry<>(e1.getKey(), (Object) e1.getValue())).collect(() -> { Map<String, Object> m = new HashMap<>(); return m; }, (m, e) -> m.put(e.getKey(), (Object) e.getValue()), Map::putAll)))).collect(() -> { Map<String, Map<String, Object>> m = new HashMap<>(); return m; }, (m, e) -> m.put(e.getKey(), (Map<String, Object>) e.getValue()), Map::putAll))) : new Optional_<>();
        
    };
    
    public Optional_<Map<String, Map<String, Object>>> objNullObj() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("objNullObj!") ? new Optional_<Map<String, Map<String, Object>>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("objNullObj!"), d0 -> d0 == null ? null : ((Map<String, ?>) d0).entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), Utility_.let(e0.getValue(), d1 -> d1 == null ? null : ((Map<String, ?>) d1).entrySet().stream().map(e1 -> new AbstractMap.SimpleEntry<>(e1.getKey(), (Object) e1.getValue())).collect(() -> { Map<String, Object> m = new HashMap<>(); return m; }, (m, e) -> m.put(e.getKey(), (Object) e.getValue()), Map::putAll)))).collect(() -> { Map<String, Map<String, Object>> m = new HashMap<>(); return m; }, (m, e) -> m.put(e.getKey(), (Map<String, Object>) e.getValue()), Map::putAll))) : new Optional_<>();
        
    };
    
    public Optional_<Object> any() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("any!") ? new Optional_<Object>((Object) ((Map<String, Object>) this.pseudoJson).get("any!")) : new Optional_<>();
        
    };
    
    public Optional_<Object> nullAny() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("nullAny!") ? new Optional_<Object>((Object) ((Map<String, Object>) this.pseudoJson).get("nullAny!")) : new Optional_<>();
        
    };
    
    public Optional_<List<Object>> arrAny() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("arrAny!") ? new Optional_<List<Object>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("arrAny!"), d0 -> d0 == null ? null : ((List<?>) d0).stream().map(e0 -> (Object) e0).toList())) : new Optional_<>();
        
    };
    
    public Optional_<List<Object>> arrNullAny() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("arrNullAny!") ? new Optional_<List<Object>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("arrNullAny!"), d0 -> d0 == null ? null : ((List<?>) d0).stream().map(e0 -> (Object) e0).toList())) : new Optional_<>();
        
    };
    
    public Optional_<Map<String, Object>> objAny() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("objAny!") ? new Optional_<Map<String, Object>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("objAny!"), d0 -> d0 == null ? null : ((Map<String, ?>) d0).entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), (Object) e0.getValue())).collect(() -> { Map<String, Object> m = new HashMap<>(); return m; }, (m, e) -> m.put(e.getKey(), (Object) e.getValue()), Map::putAll))) : new Optional_<>();
        
    };
    
    public Optional_<Map<String, Object>> objNullAny() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("objNullAny!") ? new Optional_<Map<String, Object>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("objNullAny!"), d0 -> d0 == null ? null : ((Map<String, ?>) d0).entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), (Object) e0.getValue())).collect(() -> { Map<String, Object> m = new HashMap<>(); return m; }, (m, e) -> m.put(e.getKey(), (Object) e.getValue()), Map::putAll))) : new Optional_<>();
        
    };
    
    public Optional_<ExStruct> struct() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("struct!") ? new Optional_<ExStruct>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("struct!"), d0 -> d0 == null ? null : new ExStruct((Map<String, Object>) d0))) : new Optional_<>();
        
    };
    
    public Optional_<ExStruct> nullStruct() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("nullStruct!") ? new Optional_<ExStruct>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("nullStruct!"), d0 -> d0 == null ? null : new ExStruct((Map<String, Object>) d0))) : new Optional_<>();
        
    };
    
    public Optional_<List<ExStruct>> arrStruct() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("arrStruct!") ? new Optional_<List<ExStruct>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("arrStruct!"), d0 -> d0 == null ? null : ((List<?>) d0).stream().map(e0 -> Utility_.let(e0, d1 -> d1 == null ? null : new ExStruct((Map<String, Object>) d1))).toList())) : new Optional_<>();
        
    };
    
    public Optional_<List<ExStruct>> arrNullStruct() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("arrNullStruct!") ? new Optional_<List<ExStruct>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("arrNullStruct!"), d0 -> d0 == null ? null : ((List<?>) d0).stream().map(e0 -> Utility_.let(e0, d1 -> d1 == null ? null : new ExStruct((Map<String, Object>) d1))).toList())) : new Optional_<>();
        
    };
    
    public Optional_<Map<String, ExStruct>> objStruct() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("objStruct!") ? new Optional_<Map<String, ExStruct>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("objStruct!"), d0 -> d0 == null ? null : ((Map<String, ?>) d0).entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), Utility_.let(e0.getValue(), d1 -> d1 == null ? null : new ExStruct((Map<String, Object>) d1)))).collect(() -> { Map<String, ExStruct> m = new HashMap<>(); return m; }, (m, e) -> m.put(e.getKey(), (ExStruct) e.getValue()), Map::putAll))) : new Optional_<>();
        
    };
    
    public Optional_<Map<String, ExStruct>> objNullStruct() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("objNullStruct!") ? new Optional_<Map<String, ExStruct>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("objNullStruct!"), d0 -> d0 == null ? null : ((Map<String, ?>) d0).entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), Utility_.let(e0.getValue(), d1 -> d1 == null ? null : new ExStruct((Map<String, Object>) d1)))).collect(() -> { Map<String, ExStruct> m = new HashMap<>(); return m; }, (m, e) -> m.put(e.getKey(), (ExStruct) e.getValue()), Map::putAll))) : new Optional_<>();
        
    };
    
    public Optional_<ExUnion> union() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("union!") ? new Optional_<ExUnion>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("union!"), d0 -> d0 == null ? null : new ExUnion((Map<String, Object>) d0))) : new Optional_<>();
        
    };
    
    public Optional_<ExUnion> nullUnion() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("nullUnion!") ? new Optional_<ExUnion>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("nullUnion!"), d0 -> d0 == null ? null : new ExUnion((Map<String, Object>) d0))) : new Optional_<>();
        
    };
    
    public Optional_<List<ExUnion>> arrUnion() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("arrUnion!") ? new Optional_<List<ExUnion>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("arrUnion!"), d0 -> d0 == null ? null : ((List<?>) d0).stream().map(e0 -> Utility_.let(e0, d1 -> d1 == null ? null : new ExUnion((Map<String, Object>) d1))).toList())) : new Optional_<>();
        
    };
    
    public Optional_<List<ExUnion>> arrNullUnion() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("arrNullUnion!") ? new Optional_<List<ExUnion>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("arrNullUnion!"), d0 -> d0 == null ? null : ((List<?>) d0).stream().map(e0 -> Utility_.let(e0, d1 -> d1 == null ? null : new ExUnion((Map<String, Object>) d1))).toList())) : new Optional_<>();
        
    };
    
    public Optional_<Map<String, ExUnion>> objUnion() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("objUnion!") ? new Optional_<Map<String, ExUnion>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("objUnion!"), d0 -> d0 == null ? null : ((Map<String, ?>) d0).entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), Utility_.let(e0.getValue(), d1 -> d1 == null ? null : new ExUnion((Map<String, Object>) d1)))).collect(() -> { Map<String, ExUnion> m = new HashMap<>(); return m; }, (m, e) -> m.put(e.getKey(), (ExUnion) e.getValue()), Map::putAll))) : new Optional_<>();
        
    };
    
    public Optional_<Map<String, ExUnion>> objNullUnion() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("objNullUnion!") ? new Optional_<Map<String, ExUnion>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("objNullUnion!"), d0 -> d0 == null ? null : ((Map<String, ?>) d0).entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), Utility_.let(e0.getValue(), d1 -> d1 == null ? null : new ExUnion((Map<String, Object>) d1)))).collect(() -> { Map<String, ExUnion> m = new HashMap<>(); return m; }, (m, e) -> m.put(e.getKey(), (ExUnion) e.getValue()), Map::putAll))) : new Optional_<>();
        
    };
    
    public Optional_<example.Input> fn() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("fn!") ? new Optional_<example.Input>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("fn!"), d0 -> d0 == null ? null : new example.Input((Map<String, Object>) d0))) : new Optional_<>();
        
    };
    
    public Optional_<example.Input> nullFn() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("nullFn!") ? new Optional_<example.Input>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("nullFn!"), d0 -> d0 == null ? null : new example.Input((Map<String, Object>) d0))) : new Optional_<>();
        
    };
    
    public Optional_<List<example.Input>> arrFn() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("arrFn!") ? new Optional_<List<example.Input>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("arrFn!"), d0 -> d0 == null ? null : ((List<?>) d0).stream().map(e0 -> Utility_.let(e0, d1 -> d1 == null ? null : new example.Input((Map<String, Object>) d1))).toList())) : new Optional_<>();
        
    };
    
    public Optional_<List<example.Input>> arrNullFn() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("arrNullFn!") ? new Optional_<List<example.Input>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("arrNullFn!"), d0 -> d0 == null ? null : ((List<?>) d0).stream().map(e0 -> Utility_.let(e0, d1 -> d1 == null ? null : new example.Input((Map<String, Object>) d1))).toList())) : new Optional_<>();
        
    };
    
    public Optional_<Map<String, example.Input>> objFn() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("objFn!") ? new Optional_<Map<String, example.Input>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("objFn!"), d0 -> d0 == null ? null : ((Map<String, ?>) d0).entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), Utility_.let(e0.getValue(), d1 -> d1 == null ? null : new example.Input((Map<String, Object>) d1)))).collect(() -> { Map<String, example.Input> m = new HashMap<>(); return m; }, (m, e) -> m.put(e.getKey(), (example.Input) e.getValue()), Map::putAll))) : new Optional_<>();
        
    };
    
    public Optional_<Map<String, example.Input>> objNullFn() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("objNullFn!") ? new Optional_<Map<String, example.Input>>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("objNullFn!"), d0 -> d0 == null ? null : ((Map<String, ?>) d0).entrySet().stream().map(e0 -> new AbstractMap.SimpleEntry<>(e0.getKey(), Utility_.let(e0.getValue(), d1 -> d1 == null ? null : new example.Input((Map<String, Object>) d1)))).collect(() -> { Map<String, example.Input> m = new HashMap<>(); return m; }, (m, e) -> m.put(e.getKey(), (example.Input) e.getValue()), Map::putAll))) : new Optional_<>();
        
    };
    

    public static class Builder {
        private Optional_<Boolean> bool = new Optional_<>();
        private Optional_<Boolean> nullBool = new Optional_<>();
        private Optional_<List<Boolean>> arrBool = new Optional_<>();
        private Optional_<List<Boolean>> arrNullBool = new Optional_<>();
        private Optional_<Map<String, Boolean>> objBool = new Optional_<>();
        private Optional_<Map<String, Boolean>> objNullBool = new Optional_<>();
        private Optional_<Long> int_ = new Optional_<>();
        private Optional_<Long> nullInt = new Optional_<>();
        private Optional_<List<Long>> arrInt = new Optional_<>();
        private Optional_<List<Long>> arrNullInt = new Optional_<>();
        private Optional_<Map<String, Long>> objInt = new Optional_<>();
        private Optional_<Map<String, Long>> objNullInt = new Optional_<>();
        private Optional_<Number> num = new Optional_<>();
        private Optional_<Number> nullNum = new Optional_<>();
        private Optional_<List<Number>> arrNum = new Optional_<>();
        private Optional_<List<Number>> arrNullNum = new Optional_<>();
        private Optional_<Map<String, Number>> objNum = new Optional_<>();
        private Optional_<Map<String, Number>> objNullNum = new Optional_<>();
        private Optional_<String> str = new Optional_<>();
        private Optional_<String> nullStr = new Optional_<>();
        private Optional_<List<String>> arrStr = new Optional_<>();
        private Optional_<List<String>> arrNullStr = new Optional_<>();
        private Optional_<Map<String, String>> objStr = new Optional_<>();
        private Optional_<Map<String, String>> objNullStr = new Optional_<>();
        private Optional_<List<Object>> arr = new Optional_<>();
        private Optional_<List<Object>> nullArr = new Optional_<>();
        private Optional_<List<List<Object>>> arrArr = new Optional_<>();
        private Optional_<List<List<Object>>> arrNullArr = new Optional_<>();
        private Optional_<Map<String, List<Object>>> objArr = new Optional_<>();
        private Optional_<Map<String, List<Object>>> objNullArr = new Optional_<>();
        private Optional_<Map<String, Object>> obj = new Optional_<>();
        private Optional_<Map<String, Object>> nullObj = new Optional_<>();
        private Optional_<List<Map<String, Object>>> arrObj = new Optional_<>();
        private Optional_<List<Map<String, Object>>> arrNullObj = new Optional_<>();
        private Optional_<Map<String, Map<String, Object>>> objObj = new Optional_<>();
        private Optional_<Map<String, Map<String, Object>>> objNullObj = new Optional_<>();
        private Optional_<Object> any = new Optional_<>();
        private Optional_<Object> nullAny = new Optional_<>();
        private Optional_<List<Object>> arrAny = new Optional_<>();
        private Optional_<List<Object>> arrNullAny = new Optional_<>();
        private Optional_<Map<String, Object>> objAny = new Optional_<>();
        private Optional_<Map<String, Object>> objNullAny = new Optional_<>();
        private Optional_<ExStruct> struct = new Optional_<>();
        private Optional_<ExStruct> nullStruct = new Optional_<>();
        private Optional_<List<ExStruct>> arrStruct = new Optional_<>();
        private Optional_<List<ExStruct>> arrNullStruct = new Optional_<>();
        private Optional_<Map<String, ExStruct>> objStruct = new Optional_<>();
        private Optional_<Map<String, ExStruct>> objNullStruct = new Optional_<>();
        private Optional_<ExUnion> union = new Optional_<>();
        private Optional_<ExUnion> nullUnion = new Optional_<>();
        private Optional_<List<ExUnion>> arrUnion = new Optional_<>();
        private Optional_<List<ExUnion>> arrNullUnion = new Optional_<>();
        private Optional_<Map<String, ExUnion>> objUnion = new Optional_<>();
        private Optional_<Map<String, ExUnion>> objNullUnion = new Optional_<>();
        private Optional_<example.Input> fn = new Optional_<>();
        private Optional_<example.Input> nullFn = new Optional_<>();
        private Optional_<List<example.Input>> arrFn = new Optional_<>();
        private Optional_<List<example.Input>> arrNullFn = new Optional_<>();
        private Optional_<Map<String, example.Input>> objFn = new Optional_<>();
        private Optional_<Map<String, example.Input>> objNullFn = new Optional_<>();
        public Builder() {
        }
        public Builder bool(Boolean bool) {
            this.bool = new Optional_<>(bool);
            return this;
        }
        public Builder nullBool(Boolean nullBool) {
            this.nullBool = new Optional_<>(nullBool);
            return this;
        }
        public Builder arrBool(List<Boolean> arrBool) {
            this.arrBool = new Optional_<>(arrBool);
            return this;
        }
        public Builder arrNullBool(List<Boolean> arrNullBool) {
            this.arrNullBool = new Optional_<>(arrNullBool);
            return this;
        }
        public Builder objBool(Map<String, Boolean> objBool) {
            this.objBool = new Optional_<>(objBool);
            return this;
        }
        public Builder objNullBool(Map<String, Boolean> objNullBool) {
            this.objNullBool = new Optional_<>(objNullBool);
            return this;
        }
        public Builder int_(Long int_) {
            this.int_ = new Optional_<>(int_);
            return this;
        }
        public Builder nullInt(Long nullInt) {
            this.nullInt = new Optional_<>(nullInt);
            return this;
        }
        public Builder arrInt(List<Long> arrInt) {
            this.arrInt = new Optional_<>(arrInt);
            return this;
        }
        public Builder arrNullInt(List<Long> arrNullInt) {
            this.arrNullInt = new Optional_<>(arrNullInt);
            return this;
        }
        public Builder objInt(Map<String, Long> objInt) {
            this.objInt = new Optional_<>(objInt);
            return this;
        }
        public Builder objNullInt(Map<String, Long> objNullInt) {
            this.objNullInt = new Optional_<>(objNullInt);
            return this;
        }
        public Builder num(Number num) {
            this.num = new Optional_<>(num);
            return this;
        }
        public Builder nullNum(Number nullNum) {
            this.nullNum = new Optional_<>(nullNum);
            return this;
        }
        public Builder arrNum(List<Number> arrNum) {
            this.arrNum = new Optional_<>(arrNum);
            return this;
        }
        public Builder arrNullNum(List<Number> arrNullNum) {
            this.arrNullNum = new Optional_<>(arrNullNum);
            return this;
        }
        public Builder objNum(Map<String, Number> objNum) {
            this.objNum = new Optional_<>(objNum);
            return this;
        }
        public Builder objNullNum(Map<String, Number> objNullNum) {
            this.objNullNum = new Optional_<>(objNullNum);
            return this;
        }
        public Builder str(String str) {
            this.str = new Optional_<>(str);
            return this;
        }
        public Builder nullStr(String nullStr) {
            this.nullStr = new Optional_<>(nullStr);
            return this;
        }
        public Builder arrStr(List<String> arrStr) {
            this.arrStr = new Optional_<>(arrStr);
            return this;
        }
        public Builder arrNullStr(List<String> arrNullStr) {
            this.arrNullStr = new Optional_<>(arrNullStr);
            return this;
        }
        public Builder objStr(Map<String, String> objStr) {
            this.objStr = new Optional_<>(objStr);
            return this;
        }
        public Builder objNullStr(Map<String, String> objNullStr) {
            this.objNullStr = new Optional_<>(objNullStr);
            return this;
        }
        public Builder arr(List<Object> arr) {
            this.arr = new Optional_<>(arr);
            return this;
        }
        public Builder nullArr(List<Object> nullArr) {
            this.nullArr = new Optional_<>(nullArr);
            return this;
        }
        public Builder arrArr(List<List<Object>> arrArr) {
            this.arrArr = new Optional_<>(arrArr);
            return this;
        }
        public Builder arrNullArr(List<List<Object>> arrNullArr) {
            this.arrNullArr = new Optional_<>(arrNullArr);
            return this;
        }
        public Builder objArr(Map<String, List<Object>> objArr) {
            this.objArr = new Optional_<>(objArr);
            return this;
        }
        public Builder objNullArr(Map<String, List<Object>> objNullArr) {
            this.objNullArr = new Optional_<>(objNullArr);
            return this;
        }
        public Builder obj(Map<String, Object> obj) {
            this.obj = new Optional_<>(obj);
            return this;
        }
        public Builder nullObj(Map<String, Object> nullObj) {
            this.nullObj = new Optional_<>(nullObj);
            return this;
        }
        public Builder arrObj(List<Map<String, Object>> arrObj) {
            this.arrObj = new Optional_<>(arrObj);
            return this;
        }
        public Builder arrNullObj(List<Map<String, Object>> arrNullObj) {
            this.arrNullObj = new Optional_<>(arrNullObj);
            return this;
        }
        public Builder objObj(Map<String, Map<String, Object>> objObj) {
            this.objObj = new Optional_<>(objObj);
            return this;
        }
        public Builder objNullObj(Map<String, Map<String, Object>> objNullObj) {
            this.objNullObj = new Optional_<>(objNullObj);
            return this;
        }
        public Builder any(Object any) {
            this.any = new Optional_<>(any);
            return this;
        }
        public Builder nullAny(Object nullAny) {
            this.nullAny = new Optional_<>(nullAny);
            return this;
        }
        public Builder arrAny(List<Object> arrAny) {
            this.arrAny = new Optional_<>(arrAny);
            return this;
        }
        public Builder arrNullAny(List<Object> arrNullAny) {
            this.arrNullAny = new Optional_<>(arrNullAny);
            return this;
        }
        public Builder objAny(Map<String, Object> objAny) {
            this.objAny = new Optional_<>(objAny);
            return this;
        }
        public Builder objNullAny(Map<String, Object> objNullAny) {
            this.objNullAny = new Optional_<>(objNullAny);
            return this;
        }
        public Builder struct(ExStruct struct) {
            this.struct = new Optional_<>(struct);
            return this;
        }
        public Builder nullStruct(ExStruct nullStruct) {
            this.nullStruct = new Optional_<>(nullStruct);
            return this;
        }
        public Builder arrStruct(List<ExStruct> arrStruct) {
            this.arrStruct = new Optional_<>(arrStruct);
            return this;
        }
        public Builder arrNullStruct(List<ExStruct> arrNullStruct) {
            this.arrNullStruct = new Optional_<>(arrNullStruct);
            return this;
        }
        public Builder objStruct(Map<String, ExStruct> objStruct) {
            this.objStruct = new Optional_<>(objStruct);
            return this;
        }
        public Builder objNullStruct(Map<String, ExStruct> objNullStruct) {
            this.objNullStruct = new Optional_<>(objNullStruct);
            return this;
        }
        public Builder union(ExUnion union) {
            this.union = new Optional_<>(union);
            return this;
        }
        public Builder nullUnion(ExUnion nullUnion) {
            this.nullUnion = new Optional_<>(nullUnion);
            return this;
        }
        public Builder arrUnion(List<ExUnion> arrUnion) {
            this.arrUnion = new Optional_<>(arrUnion);
            return this;
        }
        public Builder arrNullUnion(List<ExUnion> arrNullUnion) {
            this.arrNullUnion = new Optional_<>(arrNullUnion);
            return this;
        }
        public Builder objUnion(Map<String, ExUnion> objUnion) {
            this.objUnion = new Optional_<>(objUnion);
            return this;
        }
        public Builder objNullUnion(Map<String, ExUnion> objNullUnion) {
            this.objNullUnion = new Optional_<>(objNullUnion);
            return this;
        }
        public Builder fn(example.Input fn) {
            this.fn = new Optional_<>(fn);
            return this;
        }
        public Builder nullFn(example.Input nullFn) {
            this.nullFn = new Optional_<>(nullFn);
            return this;
        }
        public Builder arrFn(List<example.Input> arrFn) {
            this.arrFn = new Optional_<>(arrFn);
            return this;
        }
        public Builder arrNullFn(List<example.Input> arrNullFn) {
            this.arrNullFn = new Optional_<>(arrNullFn);
            return this;
        }
        public Builder objFn(Map<String, example.Input> objFn) {
            this.objFn = new Optional_<>(objFn);
            return this;
        }
        public Builder objNullFn(Map<String, example.Input> objNullFn) {
            this.objNullFn = new Optional_<>(objNullFn);
            return this;
        }
        public Value build() {
            return Value.fromTyped(this);
        }
    }
}
