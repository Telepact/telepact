import java.util.List;
import java.util.Map;

public class struct.Struct2 {
    public final List&lt;integer&gt; int;
    public final List&lt;integer?&gt; nullInt;
    public final List&lt;array&gt; arrInt;
    public final List&lt;array&gt; arrNullInt;
    public final List&lt;object&gt; objInt;
    public final List&lt;object&gt; objNullInt;
    public final List&lt;integer&gt; optInt!;
    public final List&lt;integer?&gt; optNullInt!;
    public final List&lt;array&gt; optArrInt!;
    public final List&lt;array&gt; optArrNullInt!;
    public final List&lt;object&gt; optObjInt!;
    public final List&lt;object&gt; optObjNullInt!;

    public struct.Struct2(List&lt;integer&gt; int, List&lt;integer?&gt; nullInt, List&lt;array&gt; arrInt, List&lt;array&gt; arrNullInt, List&lt;object&gt; objInt, List&lt;object&gt; objNullInt, List&lt;integer&gt; optInt!, List&lt;integer?&gt; optNullInt!, List&lt;array&gt; optArrInt!, List&lt;array&gt; optArrNullInt!, List&lt;object&gt; optObjInt!, List&lt;object&gt; optObjNullInt!, ) {
        this.int = int;
        this.nullInt = nullInt;
        this.arrInt = arrInt;
        this.arrNullInt = arrNullInt;
        this.objInt = objInt;
        this.objNullInt = objNullInt;
        this.optInt! = optInt!;
        this.optNullInt! = optNullInt!;
        this.optArrInt! = optArrInt!;
        this.optArrNullInt! = optArrNullInt!;
        this.optObjInt! = optObjInt!;
        this.optObjNullInt! = optObjNullInt!;
    }
}