//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

package schema

import (
	"embed"
	"fmt"
	"path"
)

//go:embed do_not_edit/*.json
var embeddedSchemas embed.FS

func loadBundledSchema(filename string) (string, error) {
	bytes, err := embeddedSchemas.ReadFile(path.Join("do_not_edit", filename))
	if err != nil {
		return "", fmt.Errorf("telepact: failed to read bundled schema %s: %w", filename, err)
	}

	return string(bytes), nil
}
