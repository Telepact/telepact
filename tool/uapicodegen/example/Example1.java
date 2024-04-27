package example;

import java.util.List;
import java.util.Map;

public class Example1 {
    public final Boolean bool;
    public final Boolean nullBool;
    public final List<Boolean> arrBool;
    public final List<Boolean> arrNullBool;
    public final Map<String, Boolean> objBool;
    public final Map<String, Boolean> objNullBool;

    public Example1(Boolean bool, Boolean nullBool, List<Boolean> arrBool, List<Boolean> arrNullBool,
            Map<String, Boolean> objBool, Map<String, Boolean> objNullBool) {
        this.bool = bool;
        this.nullBool = nullBool;
        this.arrBool = arrBool;
        this.arrNullBool = arrNullBool;
        this.objBool = objBool;
        this.objNullBool = objNullBool;
    }

}