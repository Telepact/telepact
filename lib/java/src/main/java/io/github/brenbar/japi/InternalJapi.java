package io.github.brenbar.japi;

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
}
