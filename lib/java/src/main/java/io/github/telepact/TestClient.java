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

package io.github.telepact;

import static io.github.telepact.internal.mock.IsSubMap.isSubMap;

import java.util.Map;

/**
 * A telepact client to be used in tests.
 */
public class TestClient {

    private final Client client;

    /**
     * Create a test client with the given client.
     *
     * @param client The client
     */
    public TestClient(Client client) {
        this.client = client;
    }

    /**
     * Assert that a request message sent to the client matches or does not match
     * the expected pseudo-json body.
     *
     * @param requestMessage       The request message to send
     * @param expectedPseudoJsonBody The expected pseudo-json body to match against
     * @param expectMatch          Whether to expect a match or not
     * @return The response body if a match was expected and found, or the expected
     *         body if no match was expected and none was found
     * @throws AssertionError if the expectation is not met
     */
    public Map<String, Object> assertRequest(Message requestMessage, Map<String, Object> expectedPseudoJsonBody, boolean expectMatch) {
        final var result = client.request(requestMessage);

        final var didMatch = isSubMap(expectedPseudoJsonBody, result.body);

        if (expectMatch) {
            if (!didMatch) {
                throw new AssertionError("Expected response body to match");
            } else {
                return result.body;
            }
        } else {
            if (didMatch) {
                throw new AssertionError("Expected response body to not match");
            } else {
                return expectedPseudoJsonBody;
            }
        }
    }
}
