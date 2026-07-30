#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

class MockInvocation:
    def __init__(self, function_name: str, function_argument: dict[str, object]):
        self.function_name = function_name
        self.function_argument = function_argument
        self.verified = False
