//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package telepact

// FunctionRoute processes a request message for a target function and returns a response message.
type FunctionRoute func(functionName string, requestMessage Message) (Message, error)

// FunctionRouter routes a request message to the configured function route for its body target.
type FunctionRouter struct {
	functionRoutes map[string]FunctionRoute
}

// NewFunctionRouter constructs a FunctionRouter from the supplied routes.
func NewFunctionRouter(functionRoutes map[string]FunctionRoute) *FunctionRouter {
	clonedRoutes := make(map[string]FunctionRoute, len(functionRoutes))
	for functionName, functionRoute := range functionRoutes {
		clonedRoutes[functionName] = functionRoute
	}
	return &FunctionRouter{
		functionRoutes: clonedRoutes,
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
