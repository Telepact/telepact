package uapitest;

import java.util.AbstractMap;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
    
public class Big {
    public final Map<String, Object> pseudoJson;

    public Big(Map<String, Object> pseudoJson) {
        this.pseudoJson = pseudoJson;
    }

    public static Big fromTyped(Builder b) {
        var map = new HashMap<String, Object>();
        map.put("aF", b.aF);
        map.put("cF", b.cF);
        map.put("bF", b.bF);
        map.put("dF", b.dF);
        return new Big(map);
    }

    
    public Boolean aF() {
        return (Boolean) ((Map<String, Object>) this.pseudoJson).get("aF");
        
    };
    
    public Boolean cF() {
        return (Boolean) ((Map<String, Object>) this.pseudoJson).get("cF");
        
    };
    
    public Boolean bF() {
        return (Boolean) ((Map<String, Object>) this.pseudoJson).get("bF");
        
    };
    
    public Boolean dF() {
        return (Boolean) ((Map<String, Object>) this.pseudoJson).get("dF");
        
    };
    

    public static class Builder {
        private Boolean aF;
        private Boolean cF;
        private Boolean bF;
        private Boolean dF;
        public Builder() {
        }
        public Builder aF(Boolean aF) {
            this.aF = aF;
            return this;
        }
        public Builder cF(Boolean cF) {
            this.cF = cF;
            return this;
        }
        public Builder bF(Boolean bF) {
            this.bF = bF;
            return this;
        }
        public Builder dF(Boolean dF) {
            this.dF = dF;
            return this;
        }
        public Big build() {
            return Big.fromTyped(this);
        }
    }
}
