from typing import Dict


class Handler:
    def handle(self, functionName: str, headers: Dict[str, object], input: Dict[str, object]) -> Dict[str, object]:
        pass
