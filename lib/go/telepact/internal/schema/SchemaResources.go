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
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"sync"
)

var (
	commonSchemaDirectory     string
	commonSchemaDirectoryOnce sync.Once
	commonSchemaDirectoryErr  error
)

func resolveCommonSchemaDirectory() (string, error) {
	commonSchemaDirectoryOnce.Do(func() {
		_, currentFile, _, ok := runtime.Caller(0)
		if !ok {
			commonSchemaDirectoryErr = fmt.Errorf("telepact: unable to resolve schema resource path")
			return
		}

		currentDir := filepath.Dir(currentFile)
		commonPath := filepath.Join(currentDir, "../../../../../common")
		commonSchemaDirectory = filepath.Clean(commonPath)
	})

	return commonSchemaDirectory, commonSchemaDirectoryErr
}

func loadBundledSchema(filename string) (string, error) {
	baseDir, err := resolveCommonSchemaDirectory()
	if err != nil {
		return "", err
	}

	path := filepath.Join(baseDir, filename)
	bytes, err := os.ReadFile(path)
	if err != nil {
		return "", fmt.Errorf("telepact: failed to read bundled schema %s: %w", filename, err)
	}

	return string(bytes), nil
}
