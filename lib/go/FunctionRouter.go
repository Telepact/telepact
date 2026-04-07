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

import "fmt"

// ServerFunction handles a Telepact function call using pseudo-json headers and arguments.
type ServerFunction func(headers map[string]any, arguments map[string]any) (Message, error)

// ServerMiddleware handles a Telepact request message using a function router.
type ServerMiddleware func(requestMessage Message, functionRouter *FunctionRouter) (Message, error)

type registeredFunction struct {
	authenticated bool
	handler       ServerFunction
}

// FunctionRouter routes function names to registered handlers.
type FunctionRouter struct {
	functions map[string]registeredFunction
}

// NewFunctionRouter constructs an empty FunctionRouter.
func NewFunctionRouter() *FunctionRouter {
	return &FunctionRouter{functions: map[string]registeredFunction{}}
}

// Register stores a handler for a function name.
func (r *FunctionRouter) Register(functionName string, handler ServerFunction) *FunctionRouter {
	return r.RegisterUnauthenticated(functionName, handler)
}

// RegisterUnauthenticated stores a handler for an unauthenticated function name.
func (r *FunctionRouter) RegisterUnauthenticated(functionName string, handler ServerFunction) *FunctionRouter {
	if r == nil {
		return nil
	}
	if r.functions == nil {
		r.functions = map[string]registeredFunction{}
	}
	r.functions[functionName] = registeredFunction{authenticated: false, handler: handler}
	return r
}

// RegisterAuthenticated stores a handler for an authenticated function name.
func (r *FunctionRouter) RegisterAuthenticated(functionName string, handler ServerFunction) *FunctionRouter {
	if r == nil {
		return nil
	}
	if r.functions == nil {
		r.functions = map[string]registeredFunction{}
	}
	r.functions[functionName] = registeredFunction{authenticated: true, handler: handler}
	return r
}

// Route delegates to a registered handler.
func (r *FunctionRouter) Route(requestMessage Message) (Message, error) {
	if r == nil || r.functions == nil {
		return Message{}, NewTelepactError("telepact: function router is not configured")
	}

	functionName, err := requestMessage.BodyTarget()
	if err != nil {
		return Message{}, err
	}
	arguments, err := requestMessage.BodyPayload()
	if err != nil {
		return Message{}, err
	}

	registration, ok := r.functions[functionName]
	if !ok || registration.handler == nil {
		return Message{}, NewTelepactError("telepact: unknown function " + functionName)
	}
	if registration.authenticated {
		if authResult, ok := requestMessage.Headers["@result"]; ok {
			switch typed := authResult.(type) {
			case map[string]any:
				return NewMessage(map[string]any{}, typed), nil
			case map[any]any:
				converted := make(map[string]any, len(typed))
				for key, value := range typed {
					converted[fmt.Sprint(key)] = value
				}
				return NewMessage(map[string]any{}, converted), nil
			}
		}
		if _, ok := requestMessage.Headers["@auth_"]; !ok {
			return NewMessage(map[string]any{}, map[string]any{
				"ErrorUnauthenticated_": map[string]any{
					"message!": "Valid authentication is required.",
				},
			}), nil
		}
	}
	return registration.handler(requestMessage.Headers, arguments)
}
