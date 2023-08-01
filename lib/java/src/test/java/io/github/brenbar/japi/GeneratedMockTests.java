
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
                    """
                    .trim();
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
                    """
                    .trim();
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
                    """
                    .trim();
            var expectedResult = """
                    ["fn._createStub",{},{"ok":{}}]
                    """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }

        {
            var argument = """
                    ["fn._createStub",{},{"whenFunction":"fn.test","whenArgument":{"value":{"str":"a"}},"strictMatch":false,"thenResult":{"ok":{"value":{"bool":false}}}}]
                    """
                    .trim();
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
                    """
                    .trim();
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
                    """
                    .trim();
            var expectedResult = """
                    ["fn._createStub",{},{"ok":{}}]
                    """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }

        {
            var argument = """
                    ["fn._createStub",{},{"whenFunction":"fn.test","whenArgument":{"value":{"str":"a"}},"strictMatch":true,"thenResult":{"ok":{"value":{"bool":false}}}}]
                    """
                    .trim();
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
                    """
                    .trim();
            var expectedResult = """
                    ["fn._createStub",{},{"ok":{}}]
                    """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }

        {
            var argument = """
                    ["fn._createStub",{},{"whenFunction":"fn.test","whenArgument":{"value":{"int":1,"str":"a"}},"strictMatch":true,"thenResult":{"ok":{"value":{"bool":false}}}}]
                    """
                    .trim();
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
                    """
                    .trim();
            var expectedResult = """
                    ["fn._createStub",{},{"ok":{}}]
                    """.trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }

        {
            var argument = """
                    ["fn._createStub",{},{"whenFunction":"fn.test","whenArgument":{"value":{"int":1}},"strictMatch":false,"thenResult":{"ok":{"value":{"bool":true}}}}]
                    """
                    .trim();
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
                    """
                    .trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }

        {
            var argument = """
                    ["fn.test",{"_mockEnableGeneratedStub":true},{}]
                    """.trim();
            var expectedResult = """
                    ["fn.test",{},{"ok":{"value":{"arr":["aX8SDA",225293674],"arrAny":[1948892726,1603507876],"arrBool":[],"arrEnum":[{"one":{}}],"arrFn":[{"required":false}],"arrNullArr":[null,null],"arrNullBool":[false],"arrNullEnum":[],"arrNullObj":[{"L8SPlg":851916548,"Yq3U7Q":false},{"ZZm0pQ":"UPxwKw","bQX7bg":true}],"arrNullStr":[],"arrNullStruct":[{"required":true},{"optional":true,"required":false}],"arrObj":[],"nullAny":null,"nullEnum":null,"nullFn":{"required":true},"nullInt":1627877096,"nullObj":{"HvczAA":32375166,"e4lEPQ":"es/Fgw"},"nullStr":"B+m99Q","nullStruct":{"required":true},"objAny":{},"objBool":{"ANcQqQ":false},"objFn":{},"objNullAny":{},"objNullArr":{},"objNullBool":{"P6GlHQ":null},"objNullEnum":{"Fbh2GQ":{"three":{"a":{}}},"TNFa1Q":{"one":{}}},"objNullInt":{"ParYtw":924520333},"objNullObj":{"XzYXiQ":null},"objNullStruct":{"BFW6mg":null,"drpDqA":null},"objNum":{"JqkC8g":0.37873710446323583,"ZkPyVA":0.42789261876519913},"str":"Sns37A"}}}]
                    """
                    .trim();
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
                    ["fn.test",{},{"ok":{"value":{"arrAny":[],"arrInt":[534401262,447818127],"arrNullAny":[null],"arrNullArr":[null],"arrNullBool":[true,true],"arrNullNum":[],"arrNullObj":[{"OJe1EQ":1136890999,"fIyo5A":795771906}],"arrNum":[0.25314431022045375],"arrObj":[{"Gad/iw":"KD8EgQ"},{}],"nullAny":true,"nullBool":null,"nullEnum":{"one":{}},"nullFn":{"required":false},"nullObj":null,"nullStr":"X7EB5Q","nullStruct":null,"objArr":{},"objNullAny":{},"objNullBool":{"HkLQag":true,"YRFa0Q":null},"objNullEnum":{},"objNullNum":{"U+OTCQ":null},"objNullStr":{"EE2aQQ":null,"R+goGg":"DqgtKA"},"objNullStruct":{"Ac9Rvg":null,"dpiZfQ":{"optional":true,"required":true}},"objNum":{"UtUwWA":0.4006502499474109,"XSrLyg":0.32471232553521173},"objStr":{},"objStruct":{"Rbvcsw":{"required":true}},"str":"QI2RDw"}}}]
                    """
                    .trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }

        {
            var argument = """
                    ["fn.test",{"_mockEnableGeneratedStub":true},{}]
                    """.trim();
            var expectedResult = """
                    ["fn.test",{},{"ok":{"value":{"arrBool":[true,false],"arrFn":[{"optional":true,"required":true},{"optional":true,"required":true}],"arrInt":[1854324881,1597135862],"arrNullAny":["Dj2wkw",null],"arrNullEnum":[{"two":{"optional":true,"required":false}}],"arrNullNum":[],"arrNullObj":[{"N4vsfg":"bD/iLA"},null],"arrNullStr":["civbcQ",null],"arrStruct":[{"optional":true,"required":false}],"enum":{"three":{"b":{"required":true}}},"fn":{"optional":false,"required":true},"nullAny":null,"nullArr":null,"nullBool":null,"nullFn":{"required":false},"nullInt":1394100151,"nullNum":null,"nullObj":{},"nullStruct":{"required":true},"num":0.3341164804340517,"obj":{},"objAny":{},"objEnum":{},"objInt":{"NfRpnw":20552428,"UUMOtQ":1560713546},"objNullArr":{},"objNullBool":{"NTpbhA":true,"U+/MMw":null},"objNullInt":{},"objNullStruct":{"Z/Oaxg":{"required":true}},"objNum":{},"objStr":{"f6ILlQ":"AcSEqg","fCcjfw":"fLT/TA"},"objStruct":{},"str":"Gj5Bdg"}}}]
                    """
                    .trim();
            TestUtility.generatedMockTest(argument, expectedResult, server);
        }

    }

}
