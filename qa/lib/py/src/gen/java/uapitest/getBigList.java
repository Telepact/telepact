package uapitest;

import java.util.AbstractMap;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
    
public final class getBigList {
    
    public static class Input {
        public final Map<String, Object> pseudoJson;

        public Input(Map<String, Object> pseudoJson) {
            this.pseudoJson = pseudoJson;
        }

        public static Input fromTyped(Builder b) {
            var map = new HashMap<String, Object>();
            return new Input(Map.of("fn.getBigList", map));
        }

        

        public static class Builder {
            public Builder() {
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
            return new Untyped_(tag, (Map<String, Object>) this.pseudoJson.get(tag));
        }
        
        public static Output from_Ok_(Ok_ value) {
            var map = new HashMap<String, Object>();
            map.put("Ok_", value.pseudoJson);
            return new Output(map);
        }
        
            
        public static final class Ok_ implements Output.TaggedValue {
            public final Map<String, Object> pseudoJson;

            public Ok_(Map<String, Object> pseudoJson) {
                this.pseudoJson = pseudoJson;
            }

            public static Ok_ fromTyped(Builder b) {
                var map = new HashMap<String, Object>();
                map.put("items", Utility_.let(b.items, d0 -> d0 == null ? null : d0.stream().map(e0 -> Utility_.let(e0, d1 -> d1 == null ? null : d1.pseudoJson)).toList()));
                return new Ok_(map);
            }

            
            public List<Big> items() {
                return Utility_.let(((Map<String, Object>) this.pseudoJson).get("items"), d0 -> d0 == null ? null : ((List<?>) d0).stream().map(e0 -> Utility_.let(e0, d1 -> d1 == null ? null : new Big((Map<String, Object>) d1))).toList());
                
            };
            

            public static class Builder {
                private List<Big> items;
                public Builder() {
                }
                public Builder items(List<Big> items) {
                    this.items = items;
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
