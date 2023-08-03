package io.github.brenbar.japi;

class InternalMockJApi {

  static final String JSON = """
      {
        "fn._createStub": [
          {
            "whenFunction": "string",
            "whenArgument": "object<any>",
            "thenResult": "object<any>",
            "strictMatch!": "boolean",
            "generateMissingResultFields!": "boolean"
          },
          "->",
          {
            "ok": {}
          },
          [
            "                                                                              ",
            " Create a function stub that will cause matching function calls to return the ",
            " result defined in the stub.                                                  ",
            "                                                                              "
          ]
        ],
        "enum._VerificationTimes": [
          {
            "exact": {
              "times": "integer"
            },
            "atMost": {
              "times": "integer"
            },
            "atLeast": {
              "times": "integer"
            }
          },
          [
            "                                                         ",
            " The number of times a function is allowed to be called. ",
            "                                                         "
          ]
        ],
        "fn._verify": [
          {
            "function": "string",
            "argument": "object<any>",
            "strictMatch!": "boolean",
            "times!": "enum._VerificationTimes"
          },
          "->",
          {
            "ok": {},
            "err_verificationFailure": {
              "details": "string"
            }
          },
          [
            "                                                                              ",
            " Verify an interaction occurred that matches the given verification criteria. ",
            "                                                                              "
          ]
        ],
        "fn._verifyNoMoreInteractions": [
          {},
          "->",
          {
            "ok": {},
            "err_verificationFailure": {
              "details": "string"
            }
          },
          [
            "                                                                      ",
            " Verify that no interactions have occurred with this mock or that all ",
            " interactions have been verified.                                     ",
            "                                                                      "
          ]
        ],
        "fn._clearStubs": [
          {},
          "->",
          {
            "ok": {}
          },
          [
            "                             ",
            " Clear all interaction data. ",
            "                             "
          ]
        ],
        "fn._clearInvocations": [
          {},
          "->",
          {
            "ok": {}
          },
          [
            "                            ",
            " Clear all stub conditions. ",
            "                            "
          ]
        ],
        "trait.Mockable": [
          {},
          "->",
          {
            "_errorNoMatchingStub": {}
          },
          [
            "                                                                             ",
            " If random generation is disabled, functions may return a `_noMatchingStub`  ",
            " error, indicating that the mock could not return a result for that function ",
            " call due to no matching stub being available.                               ",
            "                                                                             "
          ]
        ]
      }
      """;
}
