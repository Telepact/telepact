package uapitest;

import java.util.AbstractMap;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
    
/**
 * The main struct example.                                                        
 *                                                                                 
 * The [required] field must be supplied. The optional field does not need to be   
 * supplied.                                                                       
 */
public class ExStruct {
    public final Map<String, Object> pseudoJson;

    public ExStruct(Map<String, Object> pseudoJson) {
        this.pseudoJson = pseudoJson;
    }

    public static ExStruct fromTyped(Builder b) {
        var map = new HashMap<String, Object>();
        map.put("required", b.required);
        b.optional.ifPresent(f -> {
            map.put("optional!", f);
        });
        b.optional2.ifPresent(f -> {
            map.put("optional2!", f);
        });
        return new ExStruct(map);
    }

    
    public Boolean required() {
        return (Boolean) ((Map<String, Object>) this.pseudoJson).get("required");
        
    };
    
    public Optional_<Boolean> optional() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("optional!") ? new Optional_<Boolean>((Boolean) ((Map<String, Object>) this.pseudoJson).get("optional!")) : new Optional_<>();
        
    };
    
    public Optional_<Long> optional2() {
        return ((Map<String, Object>) this.pseudoJson).containsKey("optional2!") ? new Optional_<Long>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("optional2!"), d0 -> d0 == null ? null : d0 instanceof Integer ? ((Integer) d0).longValue() : (Long) d0)) : new Optional_<>();
        
    };
    

    public static class Builder {
        private Boolean required;
        private Optional_<Boolean> optional = new Optional_<>();
        private Optional_<Long> optional2 = new Optional_<>();
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
        public Builder optional2(Long optional2) {
            this.optional2 = new Optional_<>(optional2);
            return this;
        }
        public ExStruct build() {
            return ExStruct.fromTyped(this);
        }
    }
}
