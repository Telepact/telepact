package io.github.brenbar.japi;

class InternalJApi {

  static final String JSON = """
      {
        "function._ping": [
          {},
          "->",
          {
            "ok": {},
            "err": {
              "_unknown": {}
            }
          },
          [
            "                  ",
            " Ping the server. ",
            "                  "
          ]
        ],
        "function._schema": [
          {},
          "->",
          {
            "ok": {
              "schema": "object<any>"
            },
            "err": {
              "_unknown": {}
            }
          },
          [
            "                                       ",
            " Get the jAPI `schema` of this server. ",
            "                                       "
          ]
        ],
        "struct._ValidationFailure": [
          {
            "path": "string",
            "reason": "string"
          },
          [
            "                                                                   ",
            " A validation failure located at a `path` explained by a `reason`. ",
            "                                                                   "
          ]
        ],
        "mixin._Validation": [
          {},
          "->",
          {
            "ok": {},
            "err": {
              "_InvalidRequestTarget": {
                "reason": "string"
              },
              "_InvalidRequestHeaders": {
                "cases": "array<struct._ValidationFailure>"
              },
              "_InvalidRequestBody": {
                "cases": "array<struct._ValidationFailure>"
              },
              "_InvalidResponseBody": {
                "cases": "array<struct._ValidationFailure>"
              },
              "_ParseFailure": {
                "reason": "string"
              },
            }
          },
          [
            "                                                                                                     ",
            " All functions may return a validation error:                                                        ",
            " - `_InvalidRequestTarget`: The Target on the Request is invalid due to a `reason`                   ",
            " - `_InvalidRequestHeaders`: The Headers on the Request is invalid as outlined by a list of `cases`. ",
            " - `_InvalidRequestBody`: The Body on the Request is invalid as outlined by a list of `cases`.       ",
            " - `_InvalidResponseBody`: The Body that the Server attempted to put on the Response is invalid as   ",
            "     outlined by a list of `cases.                                                                   ",
            " - `_ParseFailure`: The Request could not be parsed as a jAPI Message.                               ",
            "                                                                                                     "
          ]
        ]
      }
      """;
}
