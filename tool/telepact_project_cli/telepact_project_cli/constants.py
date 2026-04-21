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

LICENSE_HEADER_IGNORE_FILE = ".license-header-ignore"

PROJECT_FILES = (
    "lib/java/pom.xml",
    "lib/py/pyproject.toml",
    "lib/ts/package.json",
    "bind/dart/pubspec.yaml",
    "bind/dart/package.json",
    "sdk/cli/pyproject.toml",
    "sdk/prettier/package.json",
    "sdk/console/package.json",
)

PROJECT_LABEL_MAP = {
    "lib/java": "java",
    "lib/py": "py",
    "lib/ts": "ts",
    "lib/go": "go",
    "bind/dart": "dart",
    "sdk/cli": "cli",
    "sdk/console": "console",
    "sdk/prettier": "prettier",
}

RELEASE_TARGET_ASSET_DIRECTORY_MAP = {
    "java": ["lib/java/target/central-publishing"],
    "py": ["lib/py/dist"],
    "ts": ["lib/ts/dist-tgz"],
    "dart": ["bind/dart/dist"],
    "cli": ["sdk/cli/dist", "sdk/cli/dist-docker"],
    "console": ["sdk/console/dist-tgz", "sdk/console/dist-docker"],
    "prettier": ["sdk/prettier/dist-tgz"],
}

MAX_RELEASE_ASSETS = 10

AUTOMERGE_ALLOWED_AUTHORS = ("dependabot[bot]",)

AUTOMERGE_ALLOWED_FILES = (
    "bind/dart/package-lock.json",
    "bind/dart/package.json",
    "bind/dart/pubspec.lock",
    "bind/dart/pubspec.yaml",
    "lib/java/pom.xml",
    "lib/py/uv.lock",
    "lib/py/pyproject.toml",
    "lib/ts/package-lock.json",
    "lib/ts/package.json",
    "package-lock.json",
    "package.json",
    "sdk/cli/uv.lock",
    "sdk/cli/pyproject.toml",
    "sdk/console/package-lock.json",
    "sdk/console/package.json",
    "sdk/prettier/package-lock.json",
    "sdk/prettier/package.json",
    "test/console-self-hosted/package.json",
    "test/lib/java/pom.xml",
    "test/lib/py/pyproject.toml",
    "test/lib/ts/package.json",
    "test/runner/uv.lock",
    "test/runner/pyproject.toml",
    "tool/telepact_project_cli/uv.lock",
    "tool/telepact_project_cli/pyproject.toml",
)
