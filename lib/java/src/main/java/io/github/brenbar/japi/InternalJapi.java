package io.github.brenbar.japi;

class InternalJApi {

  static final String JSON = """
      {
        "function._ping": [
          [
            "                  ",
            " Ping the server. ",
            "                  "
          ],
          [
            {},
            "-->",
            {}
          ]
        ],
        "function._schema": [
          [
            "                                       ",
            " Get the jAPI `schema` of this server. ",
            "                                       "
          ],
          [
            {},
            "-->",
            {
              "schema": "object<any>"
            }
          ]
        ],
        "struct._ValidationFailure": [
          [
            "                                                                   ",
            " A validation failure located at a `path` explained by a `reason`. ",
            "                                                                   "
          ],
          {
            "path": "string",
            "reason": "string"
          }
        ],
        "error._InvalidRequestBody": [
          [
            "                                                                                            ",
            " Indicates a failure to pass server-side validation due to invalid data in the Request Body ",
            " as explained by a list of `cases`.                                                         ",
            "                                                                                            "
          ],
          {
            "cases": "array<struct._ValidationFailure>"
          }
        ],
        "error._InvalidRequestHeaders": [
          [
            "                                                                                               ",
            " Indicates a failure to pass server-side validation due to invalid data in the Request Headers ",
            " as explained by a list of `cases`.                                                            ",
            "                                                                                               "
          ],
          {
            "cases": "array<struct._ValidationFailure>"
          }
        ],
        "error._InvalidResponseBody": [
          [
            "                                                                                             ",
            " Indicates a failure to pass server-side validation due to invalid data in the Response Body ",
            " as explained by a list of `cases`.                                                          ",
            "                                                                                             "
          ],
          {
            "cases": "array<struct._ValidationFailure>"
          }
        ],
        "error._ParseFailure": [
          [
            "                                                                ",
            " Indicates a failure for a Request to be parsed due a `reason`. ",
            "                                                                "
          ],
          {
            "reason": "string"
          }
        ],
        "error._ApplicationFailure": [
          [
            "                                                        ",
            " Indicates a failure in the application implementation. ",
            "                                                        "
          ],
          {}
        ]
      }
      """;
}
