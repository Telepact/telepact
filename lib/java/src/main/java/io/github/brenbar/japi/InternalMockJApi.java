package io.github.brenbar.japi;

class InternalMockJApi {

  static final String JSON = """
      {
        "fn._createStub": [
          {
            "whenFunctionName": "string",
            "whenArgument": "object<any>",
            "allowArgumentPartialMatch!": "boolean",
            "thenResult": "object<any>",
            "randomFillMissingResultFields!": "boolean"
          },
          "->",
          {
            "ok": {},
            "err": {
              "_unknown": {}
            }
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
            "unlimited": {},
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
            "verifyFunctionName": "string",
            "verifyArgument": "object<any>",
            "allowArgumentPartialMatch": "boolean",
            "verificationTimes": "enum._VerificationTimes"
          },
          "->",
          {
            "ok": {},
            "err": {
              "_unknown": {},
              "_verificationFailure": {
                "details": "string"
              }
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
            "err": {
              "_unknown": {},
              "_verificationFailure": {
                "details": "string"
              }
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
            "ok": {},
            "err": {
              "_unknown": {}
            }
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
            "ok": {},
            "err": {
              "_unknown": {}
            }
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
            "ok": {},
            "err": {
              "_unknown": {},
              "_noMatchingStub": {}
            }
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
