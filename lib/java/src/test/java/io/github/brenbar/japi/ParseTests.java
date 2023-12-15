package io.github.brenbar.japi;

import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.util.HashMap;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

import io.github.brenbar.japi.Server.Options;

public class ParseTests {

        private Message handle(Message requestMessage) {
                return new Message(new HashMap<>());
        }

        @Test
        public void testDuplicateKeys() throws IOException {
                var json = Files.readString(
                                FileSystems.getDefault().getPath("../../test/parse", "duplicate_keys.japi.json"));
                var e = assertThrows(JApiSchemaParseError.class, () -> new JApiSchema(json));
                Assertions.assertEquals(
                                "[{\"path\":\"\",\"reason\":{\"DuplicateSchemaKeys\":{\"keys\":[\"struct.Example\"]}}}]",
                                e.getMessage());
        }

        @Test
        public void testInvalidDefinition() throws IOException {
                var json = Files
                                .readString(FileSystems.getDefault().getPath("../../test/parse",
                                                "invalid_definition.japi.json"));
                var e = assertThrows(JApiSchemaParseError.class,
                                () -> new JApiSchema(json));
                Assertions.assertEquals(
                                "[{\"reason\":{\"DefinitionObjectMustHaveOneKeyMatchingRegex\":{\"keys\":[\"invalid.Example\"],\"regex\":\"^((fn|trait|info)|((struct|enum|ext)(<[0-2]>)?))\\\\..*\"}},\"path\":\"[0]\"}]",
                                e.getMessage());
        }

        @Test
        public void testInvalidRootBoolean() throws IOException {
                var json = Files
                                .readString(FileSystems.getDefault().getPath("../../test/parse",
                                                "invalid_root_boolean.japi.json"));
                var e = assertThrows(JApiSchemaParseError.class,
                                () -> new JApiSchema(json));
                Assertions.assertEquals(
                                "[{\"path\":\"(document-root)\",\"reason\":{\"ArrayTypeRequired\":{}}}]",
                                e.getMessage());
        }

        @Test
        public void testInvalidRootNumber() throws IOException {
                var json = Files
                                .readString(FileSystems.getDefault().getPath("../../test/parse",
                                                "invalid_root_number.japi.json"));
                var e = assertThrows(JApiSchemaParseError.class,
                                () -> new JApiSchema(json));
                Assertions.assertEquals(
                                "[{\"path\":\"(document-root)\",\"reason\":{\"ArrayTypeRequired\":{}}}]",
                                e.getMessage());
        }

        @Test
        public void testInvalidRootString() throws IOException {
                var json = Files
                                .readString(FileSystems.getDefault().getPath("../../test/parse",
                                                "invalid_root_string.japi.json"));
                var e = assertThrows(JApiSchemaParseError.class,
                                () -> new JApiSchema(json));
                Assertions.assertEquals(
                                "[{\"path\":\"(document-root)\",\"reason\":{\"ArrayTypeRequired\":{}}}]",
                                e.getMessage());
        }

        @Test
        public void testInvalidRootObject() throws IOException {
                var json = Files
                                .readString(FileSystems.getDefault().getPath("../../test/parse",
                                                "invalid_root_object.japi.json"));
                var e = assertThrows(JApiSchemaParseError.class,
                                () -> new JApiSchema(json));
                Assertions.assertEquals(
                                "[{\"path\":\"(document-root)\",\"reason\":{\"ArrayTypeRequired\":{}}}]",
                                e.getMessage());
        }

        @Test
        public void testInvalidTraitDef() throws IOException {
                var json = Files
                                .readString(FileSystems.getDefault().getPath("../../test/parse",
                                                "invalid_trait_def.japi.json"));
                var e = assertThrows(JApiSchemaParseError.class,
                                () -> new JApiSchema(json));
                Assertions.assertTrue(
                                e.getMessage().contains(
                                                "Invalid trait definition"));
        }

        @Test
        public void testInvalidTraitFnKey() throws IOException {
                var json = Files
                                .readString(FileSystems.getDefault().getPath("../../test/parse",
                                                "invalid_trait_fn_key.japi.json"));
                var e = assertThrows(JApiSchemaParseError.class,
                                () -> new JApiSchema(json));
                Assertions.assertTrue(
                                e.getMessage().contains(
                                                "Invalid trait definition"));
        }

        @Test
        public void testInvalidTraitInternalFnKey() throws IOException {
                var json = Files
                                .readString(FileSystems.getDefault().getPath("../../test/parse",
                                                "invalid_trait_internal_fn_key.japi.json"));
                var e = assertThrows(JApiSchemaParseError.class,
                                () -> new JApiSchema(json));
                Assertions.assertTrue(
                                e.getMessage().contains(
                                                "Invalid trait definition"));
        }

        @Test
        public void parseCalculatorApi() throws IOException {
                var json = Files
                                .readString(FileSystems.getDefault().getPath("../../test",
                                                "calculator.japi.json"));
                var jApi = new JApiSchema(json);
                var server = new Server(jApi, this::handle,
                                new Options().setOnError((e1) -> e1.printStackTrace()));
        }

        @Test
        public void testInvalidTraitCollideArg() throws IOException {
                var json = Files
                                .readString(FileSystems.getDefault().getPath("../../test/parse",
                                                "invalid_trait_collide_arg.japi.json"));
                var e = assertThrows(JApiSchemaParseError.class,
                                () -> new JApiSchema(json));
                Assertions.assertTrue(
                                e.getMessage().contains(
                                                "Argument field already in use"));
        }

        @Test
        public void testInvalidTraitCollideResult() throws IOException {
                var json = Files
                                .readString(FileSystems.getDefault().getPath("../../test/parse",
                                                "invalid_trait_collide_result.japi.json"));
                var e = assertThrows(JApiSchemaParseError.class,
                                () -> new JApiSchema(json));
                Assertions.assertTrue(
                                e.getMessage().contains(
                                                "Result value already in use"));
        }
}
