package io.github.brenbar.japi;

import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.util.Map;

import io.nats.client.Connection;
import io.nats.client.Dispatcher;

public class MockTestServer {

    public static Dispatcher start(Connection connection, String apiSchemaPath, String frontdoorTopic,
            Map<String, Object> config)
            throws IOException, InterruptedException {
        var json = Files.readString(FileSystems.getDefault().getPath(apiSchemaPath));
        var jApi = JApiSchema.fromJson(json);

        var options = new MockServer.Options();
        options.onError = (e) -> e.printStackTrace();
        options.enableGeneratedDefaultStub = false;

        if (config != null) {
            options.generatedCollectionLengthMin = (Integer) config.get("minLength");
            options.generatedCollectionLengthMax = (Integer) config.get("maxLength");
        }

        var server = new MockServer(jApi, options);

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

        return dispatcher;
    }
}
