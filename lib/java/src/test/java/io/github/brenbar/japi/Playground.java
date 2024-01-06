package io.github.brenbar.japi;

import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Files;

public class Playground {
    public static void main(String[] args) throws IOException {
        var json = Files.readString(FileSystems.getDefault().getPath("../../test", "example.japi.json"));
        var jApi = JApiSchema.fromJson(json);
        System.out.println("Hello world");
    }
}
