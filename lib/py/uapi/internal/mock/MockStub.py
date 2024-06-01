from typing import Dict


class MockStub:
    def __init__(self, when_function: str, when_argument: Dict[str, object],
                 then_result: Dict[str, object], allow_argument_partial_match: bool, count: int) -> None:
        self.when_function = when_function
        self.when_argument = when_argument
        self.then_result = then_result
        self.allow_argument_partial_match = allow_argument_partial_match
        self.count = count
