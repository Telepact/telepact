package uapitest;

import java.util.AbstractMap;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
    
    
public  class ExUnion {

    public final Map<String, Object> pseudoJson;

    public ExUnion(Map<String, Object> pseudoJson) {
        this.pseudoJson = pseudoJson;
    }

    public TaggedValue getTaggedValue() {
        var tag = this.pseudoJson.keySet().iterator().next();
        if (tag.equals("One")) {
            return new One((Map<String, Object>) this.pseudoJson.get(tag));
        }
        if (tag.equals("Two")) {
            return new Two((Map<String, Object>) this.pseudoJson.get(tag));
        }
        return new Untyped_(tag, (Map<String, Object>) this.pseudoJson.get(tag));
    }
    
    public static ExUnion from_One(One value) {
        var map = new HashMap<String, Object>();
        map.put("One", value.pseudoJson);
        return new ExUnion(map);
    }
    
    public static ExUnion from_Two(Two value) {
        var map = new HashMap<String, Object>();
        map.put("Two", value.pseudoJson);
        return new ExUnion(map);
    }
    
        
    public static final class One implements ExUnion.TaggedValue {
        public final Map<String, Object> pseudoJson;

        public One(Map<String, Object> pseudoJson) {
            this.pseudoJson = pseudoJson;
        }

        public static One fromTyped(Builder b) {
            var map = new HashMap<String, Object>();
            return new One(map);
        }

        

        public static class Builder {
            public Builder() {
            }
            public One build() {
                return One.fromTyped(this);
            }
        }
    }
        
    public static final class Two implements ExUnion.TaggedValue {
        public final Map<String, Object> pseudoJson;

        public Two(Map<String, Object> pseudoJson) {
            this.pseudoJson = pseudoJson;
        }

        public static Two fromTyped(Builder b) {
            var map = new HashMap<String, Object>();
            map.put("required", b.required);
            b.optional.ifPresent(f -> {
                map.put("optional!", f);
            });
            return new Two(map);
        }

        
        public Boolean required() {
            return (Boolean) ((Map<String, Object>) this.pseudoJson).get("required");
            
        };
        
        public Optional_<Boolean> optional() {
            return ((Map<String, Object>) this.pseudoJson).containsKey("optional!") ? new Optional_<Boolean>((Boolean) ((Map<String, Object>) this.pseudoJson).get("optional!")) : new Optional_<>();
            
        };
        

        public static class Builder {
            private Boolean required;
            private Optional_<Boolean> optional = new Optional_<>();
            public Builder() {
            }
            public Builder required(Boolean required) {
                this.required = required;
                return this;
            }
            public Builder optional(Boolean optional) {
                this.optional = new Optional_<>(optional);
                return this;
            }
            public Two build() {
                return Two.fromTyped(this);
            }
        }
    }
    
    public static final class Untyped_ implements ExUnion.TaggedValue {
        public final String tag;
        public final Map<String, Object> value;

        public Untyped_(String tag, Map<String, Object> value) {
            this.tag = tag;
            this.value = value;
        }
    }

    sealed interface TaggedValue {}
}
