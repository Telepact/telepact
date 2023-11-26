
    package io.github.brenbar.japi;

    import org.junit.jupiter.api.Test;

    import java.io.*;

    public class GeneratedBinaryExactTests {

    
        @Test
        public void testBinary_binary_0() throws IOException {
            var argument = new byte[] {
            (byte) 0x92, (byte) 0x81, (byte) 0xa4, (byte) 0x5f, (byte) 0x62, (byte) 0x69, (byte) 0x6e, (byte) 0x91, (byte) 0xce, (byte) 0x0, (byte) 0x0, (byte) 0x0, (byte) 0x0, (byte) 0x81, (byte) 0x0, (byte) 0x80
            };
            var expectedResult = """
            [{},{"_errorParseFailure":{"reasons":["IncompatibleBinaryEncoding"]}}]
            """.trim();
            TestUtility.testBinaryExact(argument, expectedResult);
        }
        
    }
    