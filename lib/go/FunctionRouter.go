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

package telepact

// ServerFunction handles a Telepact function call using pseudo-json headers and arguments.
type ServerFunction func(headers map[string]any, arguments map[string]any) (Message, error)

// ServerNext invokes the next server routing step.
type ServerNext func(headers map[string]any, functionName string, arguments map[string]any) (Message, error)

// ServerMiddleware handles a Telepact function call and can delegate using next.
type ServerMiddleware func(headers map[string]any, functionName string, arguments map[string]any, next ServerNext) (Message, error)

// FunctionRouter routes function names to registered handlers.
type FunctionRouter struct {
	functions map[string]ServerFunction
}

// NewFunctionRouter constructs an empty FunctionRouter.
func NewFunctionRouter() *FunctionRouter {
	return &FunctionRouter{functions: map[string]ServerFunction{}}
}

// Register stores a handler for a function name.
func (r *FunctionRouter) Register(functionName string, handler ServerFunction) *FunctionRouter {
	if r == nil {
		return nil
	}
	if r.functions == nil {
		r.functions = map[string]ServerFunction{}
	}
	r.functions[functionName] = handler
	return r
}

// Middleware delegates to a registered handler or the provided next function.
func (r *FunctionRouter) Middleware(headers map[string]any, functionName string, arguments map[string]any, next ServerNext) (Message, error) {
	if r != nil && r.functions != nil {
		if handler, ok := r.functions[functionName]; ok && handler != nil {
			return handler(headers, arguments)
		}
	}
	return next(headers, functionName, arguments)
}
