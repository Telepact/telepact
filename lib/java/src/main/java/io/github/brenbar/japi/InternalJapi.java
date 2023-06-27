package io.github.brenbar.japi;

import java.util.Map;

class InternalJApi {

  static final String JSON = """
      {
        "function._ping": [
          [],
          [
            {},
            "-->",
            {}
          ]
        ],
        "function._api": [
          [],
          [
            {},
            "-->",
            {
              "api": "object"
            }
          ]
        ],
        "struct._InvalidField": [
          [],
          {
            "field": "string",
            "reason": "string"
          }
        ],
        "error._InvalidInput": [
          [],
          {
            "cases": "array<struct._InvalidField>"
          }
        ],
        "error._InvalidOutput": [
          [],
          {}
        ],
        "error._ApplicationFailure": [
          [],
          {}
        ]
      }
      """;

  static io.github.brenbar.japi.Processor.Handler build(Map<String, Object> originalJApiDescription) {
    return (context, input) -> switch (context.functionName) {
      case "_ping" -> Map.of();
      case "_api" -> Map.of("api", originalJApiDescription);
      default -> throw new RuntimeException("Internal method not implemented");
    };
  }
}
