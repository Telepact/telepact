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
	authenticatedFunctionRoutes   map[string]FunctionRoute
	unauthenticatedFunctionRoutes map[string]FunctionRoute
}

// NewFunctionRouter constructs a FunctionRouter from the supplied function routes.
func NewFunctionRouter(authenticatedRoutes map[string]FunctionRoute, unauthenticatedRoutes ...map[string]FunctionRoute) *FunctionRouter {
	router := &FunctionRouter{
		authenticatedFunctionRoutes:   make(map[string]FunctionRoute),
		unauthenticatedFunctionRoutes: make(map[string]FunctionRoute),
	}

	if len(unauthenticatedRoutes) == 0 {
		router.RegisterUnauthenticatedRoutes(authenticatedRoutes)
		return router
	}

	router.RegisterAuthenticatedRoutes(authenticatedRoutes)
	router.RegisterUnauthenticatedRoutes(unauthenticatedRoutes[0])
	return router
}

// RegisterRoutes merges the supplied routes into the router, replacing any existing routes with the same name.
func (r *FunctionRouter) RegisterRoutes(functionRoutes map[string]FunctionRoute) {
	r.RegisterUnauthenticatedRoutes(functionRoutes)
}

// RegisterAuthenticatedRoutes merges authenticated routes into the router.
func (r *FunctionRouter) RegisterAuthenticatedRoutes(functionRoutes map[string]FunctionRoute) {
	if r == nil || functionRoutes == nil {
		return
	}
	if r.authenticatedFunctionRoutes == nil {
		r.authenticatedFunctionRoutes = make(map[string]FunctionRoute, len(functionRoutes))
	}
	for functionName, functionRoute := range functionRoutes {
		r.authenticatedFunctionRoutes[functionName] = functionRoute
		delete(r.unauthenticatedFunctionRoutes, functionName)
	}
}

// RegisterUnauthenticatedRoutes merges unauthenticated routes into the router.
func (r *FunctionRouter) RegisterUnauthenticatedRoutes(functionRoutes map[string]FunctionRoute) {
	if r == nil || functionRoutes == nil {
		return
	}
	if r.unauthenticatedFunctionRoutes == nil {
		r.unauthenticatedFunctionRoutes = make(map[string]FunctionRoute, len(functionRoutes))
	}
	for functionName, functionRoute := range functionRoutes {
		r.unauthenticatedFunctionRoutes[functionName] = functionRoute
		delete(r.authenticatedFunctionRoutes, functionName)
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

	functionRoute, ok := r.authenticatedFunctionRoutes[functionName]
	if !ok || functionRoute == nil {
		functionRoute, ok = r.unauthenticatedFunctionRoutes[functionName]
	}
	if !ok || functionRoute == nil {
		return Message{}, NewTelepactError("telepact: unknown function route for " + functionName)
	}

	return functionRoute(functionName, requestMessage)
}

// RequiresAuthentication reports whether the named route is configured as authenticated.
func (r *FunctionRouter) RequiresAuthentication(functionName string) bool {
	if r == nil {
		return false
	}
	_, ok := r.authenticatedFunctionRoutes[functionName]
	return ok
}

// HasAuthenticatedRoutes reports whether the router has any authenticated routes.
func (r *FunctionRouter) HasAuthenticatedRoutes() bool {
	return r != nil && len(r.authenticatedFunctionRoutes) > 0
}
