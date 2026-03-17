package com.example.planner;

import io.github.telepact.Client;
import io.github.telepact.Message;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.Collections;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

public final class TelepactHttpClient {
    private final HttpClient httpClient;
    private final URI uri;
    private final Client client;

    public TelepactHttpClient(String baseUrl) {
        this.httpClient = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(5)).build();
        this.uri = URI.create(baseUrl);
        Client.Options options = new Client.Options();
        options.alwaysSendJson = true;
        this.client = new Client((message, serializer) -> {
            HttpRequest request = HttpRequest.newBuilder(this.uri)
                .timeout(Duration.ofSeconds(5))
                .header("content-type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofByteArray(serializer.serialize(message)))
                .build();
            return this.httpClient.sendAsync(request, HttpResponse.BodyHandlers.ofByteArray())
                .thenApply(HttpResponse::body)
                .thenApply(serializer::deserialize);
        }, options);
    }

    public Message request(Map<String, Object> body) {
        return request(Collections.emptyMap(), body);
    }

    public Message request(Map<String, Object> headers, Map<String, Object> body) {
        return this.client.request(new Message(headers, body));
    }
}
