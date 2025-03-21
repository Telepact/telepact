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

import os
from pathlib import Path
from typing import Dict


def get_schema_file_map(directory: str) -> Dict[str, str]:
    final_json_documents: Dict[str, str] = {}

    try:
        paths = list(Path(directory).rglob("*.telepact.json"))
        for path in paths:
            with open(path, 'r') as file:
                content = file.read()
            relative_path = os.path.relpath(path, directory)
            final_json_documents[relative_path] = content
    except IOError as e:
        raise RuntimeError(e)

    return final_json_documents
