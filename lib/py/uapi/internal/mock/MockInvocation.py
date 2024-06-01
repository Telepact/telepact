from typing import Dict


class MockInvocation:
    def __init__(self, function_name: str, function_argument: Dict[str, object]):
        self.function_name = function_name
        self.function_argument = function_argument
        self.verified = False
