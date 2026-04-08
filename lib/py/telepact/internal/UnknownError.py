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

from uuid import uuid4

from ..Message import Message
from ..TelepactError import TelepactError


def ensure_unknown_case_id(error: TelepactError) -> str:
    if error.case_id is None:
        error.case_id = str(uuid4())
    return error.case_id


def build_unknown_error_message(
    error: TelepactError,
    headers: dict[str, object] | None = None,
) -> Message:
    return Message(headers or {}, {"ErrorUnknown_": {"caseId": ensure_unknown_case_id(error)}})
