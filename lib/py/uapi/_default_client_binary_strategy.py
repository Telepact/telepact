from typing import List
from threading import Lock
from dataclasses import dataclass
from datetime import datetime, timedelta
import uapi.types


@dataclass
class Checksum:
    value: int
    expiration: int


class _DefaultClientBinaryStrategy(uapi.types.ClientBinaryStrategy):

    def __init__(self):
        self.primary = None
        self.secondary = None
        self.last_update = datetime.now()
        self.lock = Lock()

    def update(self, new_checksum: int) -> None:
        with self.lock:
            if self.primary is None:
                self.primary = Checksum(new_checksum, 0)
                return

            if self.primary.value != new_checksum:
                self.secondary = self.primary
                self.primary = Checksum(new_checksum, 0)
                self.secondary.expiration += 1
                return

            self.last_update = datetime.now()

    def get_current_checksums(self) -> List[int]:
        with self.lock:
            if self.primary is None:
                return []
            elif self.secondary is None:
                return [self.primary.value]
            else:
                minutes_since_last_update = (
                    datetime.now() - self.last_update).total_seconds() / 60

                # Every 10 minute interval of non-use is a penalty point
                penalty = int(minutes_since_last_update // 10) + 1

                self.secondary.expiration += 1 * penalty

                if self.secondary.expiration > 5:
                    self.secondary = None
                    return [self.primary.value]
                else:
                    return [self.primary.value, self.secondary.value]
