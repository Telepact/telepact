package think;

import java.util.List;
import java.util.Map;

public class Ex1 {

    public Boolean field1;
    public Ex2 field2;
    public List<Boolean> field3;
    public List<Ex2> field4;
    public List<List<Ex2>> field5;
    public List<List<List<Ex2>>> field6;
    public List<Ex3<List<Ex2>>> field7;

    public Ex1(Map<String, Object> data) {
        this.field1 = (Boolean) data.get("field1");
        this.field2 = new Ex2((Map<String, Object>) data.get("field2"));
        this.field3 = ((List<Object>) data.get("field3"))
                .stream()
                .map(e -> (Boolean) e)
                .toList();
        this.field4 = ((List<Object>) data.get("field4"))
                .stream()
                .map(e -> new Ex2((Map<String, Object>) e))
                .toList();
        this.field5 = ((List<Object>) data.get("field5"))
                .stream()
                .map(e -> ((List<Object>) e)
                        .stream()
                        .map(f -> new Ex2((Map<String, Object>) f))
                        .toList())
                .toList();
        this.field6 = ((List<Object>) data.get("field6"))
                .stream()
                .map(e0 -> ((List<Object>) e0)
                        .stream()
                        .map(e1 -> ((List<Object>) e1)
                                .stream()
                                .map(e2 -> new Ex2((Map<String, Object>) e2))
                                .toList())
                        .toList())
                .toList();
        this.field7 = ((List<Object>) data.get("field7"))
                .stream()
                .map(e -> new Ex3<List<Ex2>>((Map<String, Object>) e,
                        t -> ((List<Object>) t).stream().map(t0 -> new Ex2((Map<String, Object>) t0)).toList()))
                .toList();
    }

    public static <T> List<T> newList(Object data) {
        return ((List<Object>) data)
                .stream()
                .map(e -> (T) e)
                .toList();
    }
}
