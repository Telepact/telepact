package uapitest;

import java.util.AbstractMap;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
    
public final class example {
    
    /**
     * An example function. 
     */
    public static class Input {
        public final Map<String, Object> pseudoJson;

        public Input(Map<String, Object> pseudoJson) {
            this.pseudoJson = pseudoJson;
        }

        public static Input fromTyped(Builder b) {
            var map = new HashMap<String, Object>();
            map.put("required", b.required);
            b.optional.ifPresent(f -> {
                map.put("optional!", f);
            });
            return new Input(Map.of("fn.example", map));
        }

        
        public Boolean required() {
            return (Boolean) ((Map<String, Object>) this.pseudoJson.get("fn.example")).get("required");
            
        };
        
        public Optional_<Boolean> optional() {
            return ((Map<String, Object>) this.pseudoJson.get("fn.example")).containsKey("optional!") ? new Optional_<Boolean>((Boolean) ((Map<String, Object>) this.pseudoJson.get("fn.example")).get("optional!")) : new Optional_<>();
            
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
            public Input build() {
                return Input.fromTyped(this);
            }
        }
    }
    
        
    /**
     * An example function. 
     */
    public static  class Output {

        public final Map<String, Object> pseudoJson;

        public Output(Map<String, Object> pseudoJson) {
            this.pseudoJson = pseudoJson;
        }

        public TaggedValue getTaggedValue() {
            var tag = this.pseudoJson.keySet().iterator().next();
            if (tag.equals("Ok_")) {
                return new Ok_((Map<String, Object>) this.pseudoJson.get(tag));
            }
            return new Untyped_(tag, (Map<String, Object>) this.pseudoJson.get(tag));
        }
        
        public static Output from_Ok_(Ok_ value) {
            var map = new HashMap<String, Object>();
            map.put("Ok_", value.pseudoJson);
            return new Output(map);
        }
        
            
        /**
         */
        public static final class Ok_ implements Output.TaggedValue {
            public final Map<String, Object> pseudoJson;

            public Ok_(Map<String, Object> pseudoJson) {
                this.pseudoJson = pseudoJson;
            }

            public static Ok_ fromTyped(Builder b) {
                var map = new HashMap<String, Object>();
                map.put("required", b.required);
                b.optional.ifPresent(f -> {
                    map.put("optional!", f);
                });
                return new Ok_(map);
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
                public Ok_ build() {
                    return Ok_.fromTyped(this);
                }
            }
        }
        
        public static final class Untyped_ implements Output.TaggedValue {
            public final String tag;
            public final Map<String, Object> value;

            public Untyped_(String tag, Map<String, Object> value) {
                this.tag = tag;
                this.value = value;
            }
        }

        sealed interface TaggedValue {}
    }
}
