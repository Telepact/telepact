package io.github.brenbar.japi;

import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;

import io.nats.client.Nats;

public class MockTestServer {

    public static void main(String[] givenArgs) throws IOException, InterruptedException {
        var args = givenArgs[0].split(",");

        var apiSchemaPath = args[0];
        var natsUrl = args[1];
        var frontdoorTopic = args[2];

        var json = Files.readString(FileSystems.getDefault().getPath(apiSchemaPath));
        var jApi = new JApiSchema(json);

        var server = new MockServer(jApi,
                new MockServer.Options().setOnError((e) -> e.printStackTrace()).setEnableGeneratedDefaultStub(false));

        try (var connection = Nats.connect(natsUrl)) {
            var dispatcher = connection.createDispatcher((msg) -> {
                var requestBytes = msg.getData();

                System.out.println("    ->S %s".formatted(new String(requestBytes)));
                System.out.flush();
                var responseBytes = server.process(requestBytes);
                System.out.println("    <-S %s".formatted(new String(responseBytes)));
                System.out.flush();

                connection.publish(msg.getReplyTo(), responseBytes);
            });
            dispatcher.subscribe(frontdoorTopic);

            Files.write(Path.of("MOCK_SERVER_READY"), "".getBytes(), StandardOpenOption.CREATE);
            Thread.sleep(10000000);
        }
    }
}
