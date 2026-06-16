#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import cast, NamedTuple


class Message(NamedTuple):
    headers: dict[str, object]
    body: dict[str, object]

    def get_body_target(self) -> str:
        entry = next(iter(self.body.items()))
        return entry[0]

    def get_body_payload(self) -> dict[str, object]:
        entry = next(iter(self.body.items()))
        return cast(dict[str, object], entry[1])
