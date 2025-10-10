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

import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicReference;

import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.telepact.internal.generation.GenerateContext;
import io.github.telepact.internal.types.TUnion;

/**
 * A telepact client to be used in tests.
 */
public class TestClient {

    /**
     * Options for configuring the TestClient.
     */
    public static class Options {
        /**
         * Minimum length for randomly generated arrays and objects.
         */
        public int generatedCollectionLengthMin = 0;

        /**
         * Maximum length for randomly generated arrays and objects.
         */
        public int generatedCollectionLengthMax = 3;        
    }

    private final Client client;
    private final RandomGenerator random;
    private final AtomicReference<TelepactSchema> schema;

    /**
     * Create a test client with the given client.
     *
     * @param client The client
     */
    public TestClient(Client client, Options options) {
        this.client = client;
        this.random = new RandomGenerator(options.generatedCollectionLengthMin, options.generatedCollectionLengthMax);
        this.schema = new AtomicReference<>(null);
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
    public Message assertRequest(Message requestMessage, Map<String, Object> expectedPseudoJsonBody, boolean expectMatch) {
        var s = schema.updateAndGet(nullValue -> {
            if (nullValue != null) {
                return nullValue;
            }

            var response = client.request(new Message(Map.of(), Map.of("fn.api_", Map.of())));
            var ok = (Map<String, Object>) response.body.get("Ok_");
            var api = (List<Object>) ok.get("api");
            try {
                var json = new ObjectMapper().writeValueAsString(api);
                return TelepactSchema.fromJson(json);
            } catch (Exception e) {
                throw new TelepactError(e);
            }
        });

        final var responseMessage = client.request(requestMessage);

        final var didMatch = isSubMap(expectedPseudoJsonBody, responseMessage.body);

        if (expectMatch) {
            if (!didMatch) {
                throw new AssertionError("Expected response body was not a sub map. Expected: %s Actual: %s".formatted(
                    expectedPseudoJsonBody, responseMessage.body));
            } else {
                return responseMessage;
            }
        } else {
            if (didMatch) {
                throw new AssertionError("Expected response body was a sub map. Expected: %s Actual: %s".formatted(
                    expectedPseudoJsonBody, responseMessage.body));
            } else {
                final var useBlueprintValue = true;
                final var includeOptionalFields = false;
                final var alwaysIncludeRequiredFields = true;
                final var randomizeOptionalFieldGeneration = false;

                final var functionName = (String) requestMessage.getBodyTarget();
                final var definition = (TUnion) s.parsed.get(functionName + ".->");

                final var generatedResult = (Map<String, Object>) definition.generateRandomValue(
                    expectedPseudoJsonBody, useBlueprintValue, List.of(),
                    new GenerateContext(
                            includeOptionalFields, randomizeOptionalFieldGeneration,
                            alwaysIncludeRequiredFields, functionName,
                            random));

                return new Message(responseMessage.headers, generatedResult);
            }
        }
    }

    /**
     * Set the seed for the random generator.
     * @param seed
     */
    public void setSeed(int seed) {
        this.random.setSeed(seed);
    }
}
