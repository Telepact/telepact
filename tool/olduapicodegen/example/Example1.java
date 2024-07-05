package example;

import java.util.List;
import java.util.Map;
import java.util.Optional;

public class Example1 {
    public final Boolean bool;
    public final Boolean nullBool;
    public final List<Boolean> arrBool;
    public final List<Boolean> arrNullBool;
    public final Map<String, Boolean> objBool;
    public final Map<String, Boolean> objNullBool;
    public final Optional<Boolean> optBool;
    public final NullableOptional<Boolean> optNullBool;
    public final Optional<List<Boolean>> optArrBool;
    public final Optional<List<Boolean>> optArrNullBool;
    public final Optional<Map<String, Boolean>> optObjBool;
    public final Optional<Map<String, Boolean>> optObjNullBool;

    public Example1(Boolean bool, Boolean nullBool, List<Boolean> arrBool, List<Boolean> arrNullBool,
            Map<String, Boolean> objBool, Map<String, Boolean> objNullBool, Optional<Boolean> optBool,
            NullableOptional<Boolean> optNullBool, Optional<List<Boolean>> optArrBool,
            Optional<List<Boolean>> optArrNullBool,
            Optional<Map<String, Boolean>> optObjBool, Optional<Map<String, Boolean>> optObjNullBool) {
        this.bool = bool;
        this.nullBool = nullBool;
        this.arrBool = arrBool;
        this.arrNullBool = arrNullBool;
        this.objBool = objBool;
        this.objNullBool = objNullBool;
        this.optBool = optBool;
        this.optNullBool = optNullBool;
        this.optArrBool = optArrBool;
        this.optArrNullBool = optArrNullBool;
        this.optObjBool = optObjBool;
        this.optObjNullBool = optObjNullBool;
    }
}