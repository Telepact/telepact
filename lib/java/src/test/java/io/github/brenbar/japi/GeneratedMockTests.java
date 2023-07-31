
package io.github.brenbar.japi;

import org.junit.jupiter.api.Test;

import java.io.*;

public class GeneratedMockTests {

    @Test
    public void test_testGenerate() throws IOException {

        {
            var argument = """
                    ["fn._createStub",{},{"whenFunctionName":"fn.test","whenArgument":{},"strictMatch":false,"thenResult":{"value":{"bool":true}}}]
                    """
                    .trim();
            var expectedResult = """
                    ["fn._createStub",{},{"ok":{}}]
                    """.trim();
            TestUtility.generatedMockTest(argument, expectedResult);
        }

        {
            var argument = """
                    ["fn.test",{},{}]
                    """.trim();
            var expectedResult = """
                    ["fn.test",{},{"ok":{"value":{"bool":true}}}]
                    """.trim();
            TestUtility.generatedMockTest(argument, expectedResult);
        }

    }

}
