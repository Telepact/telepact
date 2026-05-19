//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact;

/**
 * Processes a request message for a target function and returns a response
 * message.
 */
@FunctionalInterface
public interface FunctionRoute {
    Message apply(String functionName, Message requestMessage);
}
