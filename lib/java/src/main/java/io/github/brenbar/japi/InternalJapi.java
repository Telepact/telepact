package io.github.brenbar.japi;

class InternalJApi {

  static final String JSON = """
      {
        "fn._ping": [
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
        "fn._schema": [
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
        "fn._unknown": [
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
            "                                                                ",
            " A placeholder function when the requested function is unknown. ",
            "                                                                "
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
        "trait._Validated": [
          {},
          "->",
          {
            "ok": {},
            "err": {
              "_invalidRequestTarget": {
                "reason": "string"
              },
              "_invalidRequestHeaders": {
                "cases": "array<struct._ValidationFailure>"
              },
              "_invalidRequestBody": {
                "cases": "array<struct._ValidationFailure>"
              },
              "_invalidResponseBody": {
                "cases": "array<struct._ValidationFailure>"
              },
              "_parseFailure": {
                "reasons": "array<string>"
              }
            }
          },
          [
            "                                                                                                     ",
            " All functions may return a validation error:                                                        ",
            " - `_invalidRequestTarget`: The Target on the Request is invalid due to a `reason`                   ",
            " - `_invalidRequestHeaders`: The Headers on the Request is invalid as outlined by a list of `cases`. ",
            " - `_invalidRequestBody`: The Body on the Request is invalid as outlined by a list of `cases`.       ",
            " - `_invalidResponseBody`: The Body that the Server attempted to put on the Response is invalid as   ",
            "     outlined by a list of `cases.                                                                   ",
            " - `_parseFailure`: The Request could not be parsed as a jAPI Message.                               ",
            "                                                                                                     "
          ]
        ]
      }
      """;
}
