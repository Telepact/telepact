//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
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
