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

package types

// ValidateContext carries contextual state during validation traversal.
type ValidateContext struct {
	Path            []string
	Select          map[string]any
	Fn              string
	CoerceBase64    bool
	Base64Coercions map[string]any
	BytesCoercions  map[string]any
}

// NewValidateContext constructs a ValidateContext mirroring the Python implementation.
func NewValidateContext(selectStruct map[string]any, fn string, coerceBase64 bool) *ValidateContext {
	ctx := &ValidateContext{
		Path:            make([]string, 0),
		Select:          nil,
		Fn:              fn,
		CoerceBase64:    coerceBase64,
		Base64Coercions: make(map[string]any),
		BytesCoercions:  make(map[string]any),
	}

	if selectStruct != nil {
		ctx.Select = selectStruct
	}

	return ctx
}

// PushPath appends a path element to the validation context.
func (ctx *ValidateContext) PushPath(segment string) {
	if ctx == nil {
		return
	}
	ctx.Path = append(ctx.Path, segment)
}

// PopPath removes the most recent path element, if any.
func (ctx *ValidateContext) PopPath() {
	if ctx == nil || len(ctx.Path) == 0 {
		return
	}
	ctx.Path = ctx.Path[:len(ctx.Path)-1]
}

// PathString returns the current path as a dotted identifier, aiding debugging and error reporting.
func (ctx *ValidateContext) PathString() string {
	if ctx == nil || len(ctx.Path) == 0 {
		return ""
	}
	joined := ctx.Path[0]
	for i := 1; i < len(ctx.Path); i++ {
		joined += "." + ctx.Path[i]
	}
	return joined
}
