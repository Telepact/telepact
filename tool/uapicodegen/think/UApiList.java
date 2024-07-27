package think;

import java.util.ArrayList;

public class UApiList<T> extends ArrayList<T> {
    public UApiList(Object data) {
        super(((java.util.List<Object>) data)
                .stream()
                .map(T::new)
                .toList());
    }
}
