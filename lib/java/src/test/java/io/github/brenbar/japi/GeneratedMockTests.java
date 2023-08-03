
package io.github.brenbar.japi;

import org.junit.jupiter.api.Test;

import java.io.*;

public class GeneratedMockTests {


    @Test
    public void test_emptyPartialMatchStub() throws IOException {
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
            ["fn._createStub",{},{"whenFunction":"fn.test","whenArgument":{},"strictMatch":false,"thenResult":{"ok":{"value":{"bool":true}}}}]
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
    public void test_partialMatchStub() throws IOException {
        var server = TestUtility.generatedMockTestSetup();
    
        {
            var argument = """
            ["fn.test",{},{"value":{"int":1}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"int":1,"str":"a"}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn._createStub",{},{"whenFunction":"fn.test","whenArgument":{"value":{"int":1}},"strictMatch":false,"thenResult":{"ok":{"value":{"bool":true}}}}]
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
    public void test_multiplePartialMatchStub() throws IOException {
        var server = TestUtility.generatedMockTestSetup();
    
        {
            var argument = """
            ["fn.test",{},{"value":{"int":1}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"int":1,"str":"a"}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"int":0,"str":"a"}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"int":1,"str":"b"}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"bool":false,"int":1,"str":"a"}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn._createStub",{},{"whenFunction":"fn.test","whenArgument":{"value":{"int":1}},"strictMatch":false,"thenResult":{"ok":{"value":{"bool":true}}}}]
            """.trim();
            var expectedResult = """
            ["fn._createStub",{},{"ok":{}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn._createStub",{},{"whenFunction":"fn.test","whenArgument":{"value":{"str":"a"}},"strictMatch":false,"thenResult":{"ok":{"value":{"bool":false}}}}]
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
    
    @Test
    public void test_strictMatchStub() throws IOException {
        var server = TestUtility.generatedMockTestSetup();
    
        {
            var argument = """
            ["fn.test",{},{"value":{"int":1}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn._createStub",{},{"whenFunction":"fn.test","whenArgument":{"value":{"int":1}},"strictMatch":true,"thenResult":{"ok":{"value":{"bool":true}}}}]
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
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
    }
    
    @Test
    public void test_multipleStrictMatchStub() throws IOException {
        var server = TestUtility.generatedMockTestSetup();
    
        {
            var argument = """
            ["fn.test",{},{"value":{"int":1}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"str":"a"}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn._createStub",{},{"whenFunction":"fn.test","whenArgument":{"value":{"int":1}},"strictMatch":true,"thenResult":{"ok":{"value":{"bool":true}}}}]
            """.trim();
            var expectedResult = """
            ["fn._createStub",{},{"ok":{}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn._createStub",{},{"whenFunction":"fn.test","whenArgument":{"value":{"str":"a"}},"strictMatch":true,"thenResult":{"ok":{"value":{"bool":false}}}}]
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
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"str":"a"}}]
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
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"int":1,"str":"b"}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"bool":false,"int":1,"str":"a"}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
    }
    
    @Test
    public void test_mixedPartialStrictMatchStub() throws IOException {
        var server = TestUtility.generatedMockTestSetup();
    
        {
            var argument = """
            ["fn.test",{},{"value":{"int":1}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"int":1,"str":"a"}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"int":1,"str":"b"}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"bool":false,"int":1,"str":"a"}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn._createStub",{},{"whenFunction":"fn.test","whenArgument":{"value":{"int":1}},"strictMatch":false,"thenResult":{"ok":{"value":{"bool":true}}}}]
            """.trim();
            var expectedResult = """
            ["fn._createStub",{},{"ok":{}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn._createStub",{},{"whenFunction":"fn.test","whenArgument":{"value":{"int":1,"str":"a"}},"strictMatch":true,"thenResult":{"ok":{"value":{"bool":false}}}}]
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
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
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
            ["fn.test",{},{"ok":{"value":{"bool":true}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
    }
    
    @Test
    public void test_mixedStrictPartialMatchStub() throws IOException {
        var server = TestUtility.generatedMockTestSetup();
    
        {
            var argument = """
            ["fn.test",{},{"value":{"int":1}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"int":1,"str":"a"}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"int":1,"str":"b"}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"bool":false,"int":1,"str":"a"}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn._createStub",{},{"whenFunction":"fn.test","whenArgument":{"value":{"int":1,"str":"a"}},"strictMatch":true,"thenResult":{"ok":{"value":{"bool":false}}}}]
            """.trim();
            var expectedResult = """
            ["fn._createStub",{},{"ok":{}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn._createStub",{},{"whenFunction":"fn.test","whenArgument":{"value":{"int":1}},"strictMatch":false,"thenResult":{"ok":{"value":{"bool":true}}}}]
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
        
        {
            var argument = """
            ["fn.test",{},{"value":{"int":0,"str":"a"}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"err":{"_noMatchingStub":{}}}]
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
            ["fn.test",{},{"ok":{"value":{"bool":true}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
    }
    
    @Test
    public void test_generation() throws IOException {
        var server = TestUtility.generatedMockTestSetup();
    
        {
            var argument = """
            ["fn.test",{"_mockEnableGeneratedStub":true},{}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"ok":{"value":{"arrArr":[[794471793,"L+Uz1w"],[]],"arrFn":[],"arrInt":[996984527,1157490780],"arrNullEnum":[{"two":{"required":false}}],"arrNullFn":[{"optional":false,"required":true}],"arrNullInt":[],"arrNullStr":["fFlptw",null],"arrNullStruct":[{"required":false},null],"arrNum":[0.36801382462084165,0.2692544383297682],"arrObj":[],"arrStr":["L2Iupw","Ey7vVA"],"arrStruct":[],"bool":true,"fn":{"optional":true,"required":true},"int":662438587,"nullArr":null,"nullEnum":null,"nullFn":{"required":false},"nullNum":null,"nullStruct":{"required":false},"obj":{"HucnUg":"FDaLIA","dF0s2Q":false},"objArr":{},"objBool":{},"objEnum":{},"objFn":{"HyYKTQ":{"required":true},"JBL8UA":{"optional":true,"required":true}},"objNullArr":{"MGjeJg":[477410994],"fmoFaA":null},"objNullInt":{"SPhqCg":1608358040,"ULNNrA":null},"objNullStruct":{"OiQwYg":null},"objNum":{},"objObj":{"dft53A":{"VIdpug":1353996232},"fDiAYQ":{}}}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{"_mockEnableGeneratedStub":true},{}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"ok":{"value":{"arr":["aX8SDA",225293674],"arrAny":[1948892726,1603507876],"arrBool":[],"arrEnum":[{"one":{}}],"arrFn":[{"required":false}],"arrNullArr":[null,null],"arrNullBool":[false],"arrNullEnum":[],"arrNullObj":[{"L8SPlg":851916548,"Yq3U7Q":false},{"ZZm0pQ":"UPxwKw","bQX7bg":true}],"arrNullStr":[],"arrNullStruct":[{"required":true},{"optional":true,"required":false}],"arrObj":[],"nullAny":null,"nullEnum":null,"nullFn":{"required":true},"nullInt":1627877096,"nullObj":{"HvczAA":32375166,"e4lEPQ":"es/Fgw"},"nullStr":"B+m99Q","nullStruct":{"required":true},"objAny":{},"objBool":{"ANcQqQ":false},"objFn":{},"objNullAny":{},"objNullArr":{},"objNullBool":{"P6GlHQ":null},"objNullEnum":{"Fbh2GQ":{"two":{"optional":true,"required":false}},"Kyh52w":null},"objNullFn":{"ParYtw":{"required":true}},"objNullInt":{"XzYXiQ":null},"objNullObj":{"BFW6mg":null,"drpDqA":null},"objNullStr":{"LggtQw":null,"ZkPyVA":"JqkC8g"},"objObj":{"Jsm1Fg":{},"bgjntQ":{"G3ABuw":"RC1KMQ"}}}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{"_mockEnableGeneratedStub":true},{}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"ok":{"value":{"arr":[],"arrAny":["ayDPqw"],"arrEnum":[{"one":{}},{"two":{"optional":true,"required":true}}],"arrNullAny":[],"arrNullArr":[[true,2089593060]],"arrNullBool":[],"arrNullInt":[null],"arrNullNum":[0.3105464996760181,null],"enum":{"one":{}},"fn":{"required":true},"int":1465606523,"nullAny":false,"nullArr":null,"nullBool":null,"nullFn":null,"nullInt":1605435877,"nullNum":null,"num":0.2565006794084478,"objEnum":{},"objInt":{"HkLQag":1508850011,"JbdV+A":1628527313},"objNullArr":{},"objNullFn":{"U+OTCQ":null},"objNullNum":{"EE2aQQ":null,"R+goGg":0.26713475720539054},"objNullObj":{"XSrLyg":{"C5j6BA":1518930466,"dZCVsQ":1647834647},"dpiZfQ":{"A6l5QA":30364094,"ZyHiHw":409369397}},"objNullStr":{"HxOFnA":"FfW7eg","P/NJ6Q":"QI2RDw"},"objStr":{"Lmw/0g":"bfVYow","S7DsNA":"BoSaXQ"},"str":"WiqHHg"}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{"_mockEnableGeneratedStub":true},{}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"ok":{"value":{"arrAny":["XzJb9g","SIHKZA"],"arrArr":[[true,false],[361791194]],"arrBool":[],"arrEnum":[],"arrInt":[],"arrNullAny":[931916926,true],"arrNullArr":[[],null],"arrNullNum":[0.4095690122275356],"arrNullObj":[{"Lap+6w":98140897},{"SoXgYw":1919331609,"bcfs9A":2043612818}],"arrNullStr":[],"arrNum":[0.2439486607045458],"arrObj":[],"arrStr":["Nbp7JA"],"bool":false,"int":196245167,"nullBool":null,"nullEnum":null,"nullFn":{"required":true},"nullInt":null,"nullObj":null,"nullStr":null,"num":0.40672077236140625,"obj":{},"objAny":{"NTpbhA":"NWEHog","U+/MMw":"YFOFaQ"},"objBool":{},"objNullAny":{"Z/Oaxg":true},"objNullArr":{},"objNullEnum":{"f6ILlQ":null,"fCcjfw":null},"objNullFn":{},"objNullInt":{"O7gDdw":1673074765},"objNullStr":{"IZ4EBQ":"AUC+iw","VwgJTg":"WxzTfA"},"objNum":{"O3q4Zw":0.423687954362761,"S02uvQ":0.32807261708784646},"str":"WHxNXw"}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{"_mockEnableGeneratedStub":true},{}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"ok":{}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{"_mockEnableGeneratedStub":true},{}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"ok":{"value":{"arrAny":[],"arrBool":[true,true],"arrEnum":[{"one":{}},{"two":{"optional":false,"required":true}}],"arrInt":[799309190,49051207],"arrNullAny":["UO294A",true],"arrNullEnum":[{"two":{"required":true}}],"arrNullFn":[null,{"required":true}],"arrNullNum":[],"arrNullObj":[null,null],"arrNullStr":[],"arrNullStruct":[null],"arrNum":[],"enum":{"two":{"required":true}},"fn":{"required":false},"int":978763012,"nullArr":[],"nullBool":null,"nullInt":1150807595,"nullStr":"YuVvNA","nullStruct":{"required":true},"obj":{"dHNwzA":36180522},"objArr":{"MY+b0A":["PIoR7w"],"VQ0m9g":["eAtbzQ",1467486099]},"objFn":{"XdCXlA":{"optional":true,"required":false},"e+sU6A":{"optional":true,"required":false}},"objNullFn":{"Idhf+w":null,"Ui5ycQ":{"required":false}},"objNullInt":{"BVf+qQ":null,"dkzTcw":null},"objNullStruct":{"bPMnSA":{"required":false}},"objObj":{"bxF/Yw":{"C1DkGQ":"axKuvw"}},"objStr":{"ZtD46g":"Yc132w"},"objStruct":{"N+gdjQ":{"required":true},"Nz25tg":{"required":true}},"struct":{"optional":false,"required":false}}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
    }
    
    @Test
    public void test_emptyPartialMatchVerify() throws IOException {
        var server = TestUtility.generatedMockTestSetup();
    
        {
            var argument = """
            ["fn._createStub",{},{"whenFunction":"fn.test","whenArgument":{},"strictMatch":false,"thenResult":{"ok":{}}}]
            """.trim();
            var expectedResult = """
            ["fn._createStub",{},{"ok":{}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn._verify",{},{"function":"fn.test","argument":{}}]
            """.trim();
            var expectedResult = """
            ["fn._verify",{},{"err":{"_verificationFailure":{"details":"Wanted at least 1 partial match, but found 0.\\nQuery:\\nfn.test {}\\nAvailable:\\n<none>\\n"}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn._verify",{},{"function":"fn.test","argument":{},"times":{"exact":{"times":1}}}]
            """.trim();
            var expectedResult = """
            ["fn._verify",{},{"err":{"_verificationFailure":{"details":"Wanted exactly 1 partial match, but found 0.\\nQuery:\\nfn.test {}\\nAvailable:\\n<none>\\n"}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn._verify",{},{"function":"fn.test","argument":{},"times":{"atLeast":{"times":1}}}]
            """.trim();
            var expectedResult = """
            ["fn._verify",{},{"err":{"_verificationFailure":{"details":"Wanted at least 1 partial match, but found 0.\\nQuery:\\nfn.test {}\\nAvailable:\\n<none>\\n"}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn._verify",{},{"function":"fn.test","argument":{},"times":{"atMost":{"times":0}}}]
            """.trim();
            var expectedResult = """
            ["fn._verify",{},{"ok":{}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"ok":{}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn._verify",{},{"function":"fn.test","argument":{}}]
            """.trim();
            var expectedResult = """
            ["fn._verify",{},{"ok":{}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn._verify",{},{"function":"fn.test","argument":{},"times":{"exact":{"times":1}}}]
            """.trim();
            var expectedResult = """
            ["fn._verify",{},{"ok":{}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn._verify",{},{"function":"fn.test","argument":{},"times":{"atLeast":{"times":1}}}]
            """.trim();
            var expectedResult = """
            ["fn._verify",{},{"ok":{}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn._verify",{},{"function":"fn.test","argument":{},"times":{"atMost":{"times":0}}}]
            """.trim();
            var expectedResult = """
            ["fn._verify",{},{"err":{"_verificationFailure":{"details":"Wanted at most 0 partial matches, but found 1.\\nQuery:\\nfn.test {}\\nAvailable:\\nfn.test {}\\n"}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
    }
    
    @Test
    public void test_partialMatchVerify() throws IOException {
        var server = TestUtility.generatedMockTestSetup();
    
        {
            var argument = """
            ["fn._createStub",{},{"whenFunction":"fn.test","whenArgument":{},"strictMatch":false,"thenResult":{"ok":{}}}]
            """.trim();
            var expectedResult = """
            ["fn._createStub",{},{"ok":{}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn._verify",{},{"function":"fn.test","argument":{"value":{"int":0}}}]
            """.trim();
            var expectedResult = """
            ["fn._verify",{},{"err":{"_verificationFailure":{"details":"Wanted at least 1 partial match, but found 0.\\nQuery:\\nfn.test {\\"value\\":{\\"int\\":0}}\\nAvailable:\\n<none>\\n"}}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn.test",{},{"value":{"int":0}}]
            """.trim();
            var expectedResult = """
            ["fn.test",{},{"ok":{}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
        {
            var argument = """
            ["fn._verify",{},{"function":"fn.test","argument":{"value":{"int":0}}}]
            """.trim();
            var expectedResult = """
            ["fn._verify",{},{"ok":{}}]
            """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }
        
    }
    
}
