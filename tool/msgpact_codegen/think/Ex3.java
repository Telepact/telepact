package think;

import java.util.function.Function;

public class Ex3<T> {

    public final Boolean field1;
    public final T field2;

    public Ex3(Boolean field1, T field2) {
        this.field1 = field1;
        this.field2 = field2;
    }

    public Ex3(Object data, Function<Object, T> mapper0) {
        this.field1 = (Boolean) data;
        this.field2 = mapper0.apply(data);
    }

}
