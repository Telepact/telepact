package think;

import java.util.Map;

public class Ex2 {
    public final Boolean field1;
    public final String field2;

    public Ex2(Map<String, Object> data) {
        this.field1 = (Boolean) data.get("field1");
        this.field2 = (String) data.get("field2");
    }
}
