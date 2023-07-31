
package io.github.brenbar.japi;

import org.junit.jupiter.api.Test;

import java.io.*;

public class GeneratedMockTests {


    @Test
    public void test_testEmptyPartialMatchStub() throws IOException {
        var server = TestUtility.generatedMockTestSetup();
    
        {
            var argument = """
            ["fn.test",{},{}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn._createStub",{},{"whenFunctionName":"fn.test","whenArgument":{},"strictMatch":false,"thenResult":{"ok":{"value":{"bool":true}}}}]
            """.trim();
            var expectedResult = """
            ["fn._createStub",{},{"ok":{}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"ok":{"value":{"bool":true}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
    }
    
    @Test
    public void test_testPartialMatchStub() throws IOException {
        var server = TestUtility.generatedMockTestSetup();
    
        {
            var argument = """
            ["fn.test",{},{}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"int":0}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn._createStub",{},{"whenFunctionName":"fn.test","whenArgument":{"value":{"int":1}},"strictMatch":false,"thenResult":{"ok":{"value":{"bool":true}}}}]
            """.trim();
            var expectedResult = """
            ["fn._createStub",{},{"ok":{}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"int":0}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"int":1}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"ok":{"value":{"bool":true}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"int":1,"str":"a"}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"ok":{"value":{"bool":true}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
    }
    
    @Test
    public void test_testMultiplePartialMatchStub() throws IOException {
        var server = TestUtility.generatedMockTestSetup();
    
        {
            var argument = """
            ["fn.test",{},{}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"int":0}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn._createStub",{},{"whenFunctionName":"fn.test","whenArgument":{"value":{"int":1}},"strictMatch":false,"thenResult":{"ok":{"value":{"bool":true}}}}]
            """.trim();
            var expectedResult = """
            ["fn._createStub",{},{"ok":{}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn._createStub",{},{"whenFunctionName":"fn.test","whenArgument":{"value":{"str":"a"}},"strictMatch":false,"thenResult":{"ok":{"value":{"bool":false}}}}]
            """.trim();
            var expectedResult = """
            ["fn._createStub",{},{"ok":{}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"int":0}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"int":1}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"ok":{"value":{"bool":true}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"int":1,"str":"a"}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"ok":{"value":{"bool":false}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"int":0,"str":"a"}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"ok":{"value":{"bool":false}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"int":1,"str":"b"}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"ok":{"value":{"bool":true}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"bool":false,"int":1,"str":"a"}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"ok":{"value":{"bool":false}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
    }
    
}
