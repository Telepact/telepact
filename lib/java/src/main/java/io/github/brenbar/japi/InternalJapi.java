package io.github.brenbar.japi;

class InternalJApi {

  static final String JSON = """
      {
        "fn._ping": [
          {},
          "->",
          {
            "ok": {}
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
            "_err_unknown": {},
            "_err_invalidRequestTarget": {
              "reason": "string"
            },
            "_err_invalidRequestHeaders": {
              "cases": "array<struct._ValidationFailure>"
            },
            "_err_invalidRequestBody": {
              "cases": "array<struct._ValidationFailure>"
            },
            "_err_invalidResponseBody": {
              "cases": "array<struct._ValidationFailure>"
            },
            "_err_parseFailure": {
              "reasons": "array<string>"
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
