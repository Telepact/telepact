package think;

import java.util.ArrayList;

public class MsgPactList<T> extends ArrayList<T> {
    public MsgPactList(Object data) {
        super(((java.util.List<Object>) data)
                .stream()
                .map(T::new)
                .toList());
    }
}
