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

from .automerge import automerge
from .consolidated_readme import consolidated_readme
from .doc_versions import doc_versions
from .github_labels import github_labels
from .license_header import license_header
from .release import publish_targets, release
from .versioning import bump, get, set_version

COMMANDS = (
    get,
    set_version,
    bump,
    license_header,
    github_labels,
    release,
    publish_targets,
    automerge,
    consolidated_readme,
    doc_versions,
)
