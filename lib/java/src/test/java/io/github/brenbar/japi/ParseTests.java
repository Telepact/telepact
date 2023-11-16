package io.github.brenbar.japi;

import static org.junit.jupiter.api.Assertions.assertEquals;
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
        var json = Files.readString(FileSystems.getDefault().getPath("../../test/parse", "duplicate_keys.japi.json"));
        var e = assertThrows(JApiSchemaParseError.class,
                () -> new Server(json, this::handle, new Options().setOnError((e1) -> e1.printStackTrace())));
        Assertions.assertTrue(e.getMessage().contains("Final schema has duplicate keys"));
    }
}
