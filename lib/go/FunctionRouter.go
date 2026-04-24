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

// FunctionRoute processes a request message for a target function and returns a response message.
type FunctionRoute func(functionName string, requestMessage Message) (Message, error)

// FunctionRouter routes a request message to the configured function route for its body target.
type FunctionRouter struct {
	functionRoutes map[string]FunctionRoute
}

// NewFunctionRouter constructs a FunctionRouter from the supplied function routes.
func NewFunctionRouter(functionRoutes map[string]FunctionRoute) *FunctionRouter {
	clonedRoutes := make(map[string]FunctionRoute, len(functionRoutes))
	for functionName, functionRoute := range functionRoutes {
		clonedRoutes[functionName] = functionRoute
	}
	return &FunctionRouter{functionRoutes: clonedRoutes}
}

// RegisterRoutes merges the supplied routes into the router, replacing any existing routes with the same name.
func (r *FunctionRouter) RegisterRoutes(functionRoutes map[string]FunctionRoute) {
	if r == nil || functionRoutes == nil {
		return
	}
	if r.functionRoutes == nil {
		r.functionRoutes = make(map[string]FunctionRoute, len(functionRoutes))
	}
	for functionName, functionRoute := range functionRoutes {
		r.functionRoutes[functionName] = functionRoute
	}
}

// Route dispatches a request message to the configured function route for its target.
func (r *FunctionRouter) Route(requestMessage Message) (Message, error) {
	if r == nil {
		return Message{}, NewTelepactError("telepact: function router is nil")
	}

	functionName, err := requestMessage.BodyTarget()
	if err != nil {
		return Message{}, err
	}

	functionRoute, ok := r.functionRoutes[functionName]
	if !ok || functionRoute == nil {
		return Message{}, NewTelepactError("telepact: unknown function route for " + functionName)
	}

	return functionRoute(functionName, requestMessage)
}
