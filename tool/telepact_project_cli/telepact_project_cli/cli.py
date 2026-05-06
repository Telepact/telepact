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

import click

from .commands.license_header import license_header
from .commands.project_version import bump, get, set_version
from .commands.repository_automation import (
    automerge,
    mark_merge_ready,
    merge_pr,
    open_version_bump_pr,
    print_release_manifest,
    publish_targets,
    release,
)
from .commands.consolidated_readme import consolidated_readme
from .commands.doc_versions import doc_versions


@click.group()
def main() -> None:
    pass



main.add_command(get)
main.add_command(set_version)
main.add_command(bump)
main.add_command(license_header)
main.add_command(mark_merge_ready)
main.add_command(merge_pr)
main.add_command(release)
main.add_command(open_version_bump_pr)
main.add_command(publish_targets)
main.add_command(print_release_manifest)
main.add_command(automerge)
main.add_command(consolidated_readme)
main.add_command(doc_versions)

if __name__ == "__main__":
    main()
