package example;

import java.util.List;
import java.util.Map;
import java.util.Optional;

public class Example2 {
    public final Integer int_;
    public final Integer nullInt;
    public final List<Integer> arrInt;
    public final List<Integer> arrNullInt;
    public final Map<String, Integer> objInt;
    public final Map<String, Integer> objNullInt;
    public final Optional<Integer> optInt;
    public final NullableOptional<Integer> optNullInt;
    public final Optional<List<Integer>> optArrInt;
    public final Optional<List<Integer>> optArrNullInt;
    public final Optional<Map<String, Integer>> optObjInt;
    public final Optional<Map<String, Integer>> optObjNullInt;

    public Example2(Integer int_, Integer nullInt, List<Integer> arrInt, List<Integer> arrNullInt,
            Map<String, Integer> objInt, Map<String, Integer> objNullInt, Optional<Integer> optInt,
            NullableOptional<Integer> optNullInt, Optional<List<Integer>> optArrInt,
            Optional<List<Integer>> optArrNullInt,
            Optional<Map<String, Integer>> optObjInt, Optional<Map<String, Integer>> optObjNullInt) {
        this.int_ = int_;
        this.nullInt = nullInt;
        this.arrInt = arrInt;
        this.arrNullInt = arrNullInt;
        this.objInt = objInt;
        this.objNullInt = objNullInt;
        this.optInt = optInt;
        this.optNullInt = optNullInt;
        this.optArrInt = optArrInt;
        this.optArrNullInt = optArrNullInt;
        this.optObjInt = optObjInt;
        this.optObjNullInt = optObjNullInt;
    }

}
