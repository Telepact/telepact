#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

from datetime import datetime
import threading
from threading import Lock

from .BinaryEncodingCache import BinaryEncodingCache

class Checksum:
    def __init__(self, value: int, expiration: int) -> None:
        self.value = value
        self.expiration = expiration


class ClientBinaryStrategy:

    def __init__(self, binary_encoding_cache: 'BinaryEncodingCache') -> None:
        self.binary_encoding_cache = binary_encoding_cache
        self.primary: Checksum | None = None
        self.secondary: Checksum | None = None
        self.last_update = datetime.now()
        self.lock = Lock()

    def update_checksum(self, new_checksum: int) -> None:
        with self.lock:
            if self.primary is None:
                self.primary = Checksum(new_checksum, 0)
                return

            if self.primary.value != new_checksum:
                expired_checksum = self.secondary
                self.secondary = self.primary
                self.primary = Checksum(new_checksum, 0)
                self.secondary.expiration += 1

                if expired_checksum:
                    self.binary_encoding_cache.remove(expired_checksum.value)

                return

            self.last_update = datetime.now()

    def get_current_checksums(self) -> list[int]:
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
