package io.github.brenbar.japi.server;

import java.util.Map;

class InternalJapi {

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

    static Handler build(Map<String, Object> originalApiDescription) {
        return (functionName, headers, input) -> switch (functionName) {
            case "_ping" -> Map.of();
            case "_api" -> Map.of("api", originalApiDescription);
            default -> throw new Error.FunctionNotFound(functionName);
        };
    }
}
