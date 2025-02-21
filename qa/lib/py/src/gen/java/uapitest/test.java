package uapitest;

import java.util.AbstractMap;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
    
public final class test {
    
    public static class Input {
        public final Map<String, Object> pseudoJson;

        public Input(Map<String, Object> pseudoJson) {
            this.pseudoJson = pseudoJson;
        }

        public static Input fromTyped(Builder b) {
            var map = new HashMap<String, Object>();
            b.value.ifPresent(f -> {
                map.put("value!", Utility_.let(f, d0 -> d0 == null ? null : d0.pseudoJson));
            });
            return new Input(Map.of("fn.test", map));
        }

        
        public Optional_<Value> value() {
            return ((Map<String, Object>) this.pseudoJson.get("fn.test")).containsKey("value!") ? new Optional_<Value>(Utility_.let(((Map<String, Object>) this.pseudoJson.get("fn.test")).get("value!"), d0 -> d0 == null ? null : new Value((Map<String, Object>) d0))) : new Optional_<>();
            
        };
        

        public static class Builder {
            private Optional_<Value> value = new Optional_<>();
            public Builder() {
            }
            public Builder value(Value value) {
                this.value = new Optional_<>(value);
                return this;
            }
            public Input build() {
                return Input.fromTyped(this);
            }
        }
    }
    
        
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
            if (tag.equals("ErrorExample")) {
                return new ErrorExample((Map<String, Object>) this.pseudoJson.get(tag));
            }
            return new Untyped_(tag, (Map<String, Object>) this.pseudoJson.get(tag));
        }
        
        public static Output from_Ok_(Ok_ value) {
            var map = new HashMap<String, Object>();
            map.put("Ok_", value.pseudoJson);
            return new Output(map);
        }
        
        public static Output from_ErrorExample(ErrorExample value) {
            var map = new HashMap<String, Object>();
            map.put("ErrorExample", value.pseudoJson);
            return new Output(map);
        }
        
            
        public static final class Ok_ implements Output.TaggedValue {
            public final Map<String, Object> pseudoJson;

            public Ok_(Map<String, Object> pseudoJson) {
                this.pseudoJson = pseudoJson;
            }

            public static Ok_ fromTyped(Builder b) {
                var map = new HashMap<String, Object>();
                b.value.ifPresent(f -> {
                    map.put("value!", Utility_.let(f, d0 -> d0 == null ? null : d0.pseudoJson));
                });
                return new Ok_(map);
            }

            
            public Optional_<Value> value() {
                return ((Map<String, Object>) this.pseudoJson).containsKey("value!") ? new Optional_<Value>(Utility_.let(((Map<String, Object>) this.pseudoJson).get("value!"), d0 -> d0 == null ? null : new Value((Map<String, Object>) d0))) : new Optional_<>();
                
            };
            

            public static class Builder {
                private Optional_<Value> value = new Optional_<>();
                public Builder() {
                }
                public Builder value(Value value) {
                    this.value = new Optional_<>(value);
                    return this;
                }
                public Ok_ build() {
                    return Ok_.fromTyped(this);
                }
            }
        }
            
        public static final class ErrorExample implements Output.TaggedValue {
            public final Map<String, Object> pseudoJson;

            public ErrorExample(Map<String, Object> pseudoJson) {
                this.pseudoJson = pseudoJson;
            }

            public static ErrorExample fromTyped(Builder b) {
                var map = new HashMap<String, Object>();
                map.put("property", b.property);
                return new ErrorExample(map);
            }

            
            public String property() {
                return (String) ((Map<String, Object>) this.pseudoJson).get("property");
                
            };
            

            public static class Builder {
                private String property;
                public Builder() {
                }
                public Builder property(String property) {
                    this.property = property;
                    return this;
                }
                public ErrorExample build() {
                    return ErrorExample.fromTyped(this);
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
