from typing import List
from typing_extensions import Protocol

from lib.py.src.japi.client_next_process import ClientNextProcess


class ClientProcessor(Protocol):
    def process(self, japi_message: List[object], next_process: ClientNextProcess) -> List[object]:
        pass
