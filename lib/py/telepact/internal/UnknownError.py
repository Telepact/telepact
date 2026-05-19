#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from ..Message import Message
from ..TelepactError import TelepactError

def build_unknown_error_message(
    error: TelepactError,
    headers: dict[str, object] | None = None,
) -> Message:
    return Message(headers or {}, {"ErrorUnknown_": {"caseId": error.case_id}})
