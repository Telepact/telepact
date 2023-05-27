package io.github.brenbar.japi;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.List;
import java.util.Map;

public class Processor {
    interface Handler {
        Map<String, Object> handle(String functionName, Map<String, Object> headers, Map<String, Object> input);
    }

    public static class Error extends RuntimeException {
        public Error(String message) {
            super(message);
        }
        public Error(Throwable cause) {
            super(cause);
        }
    }

    public static class InvalidJson extends Error {
        public InvalidJson(Throwable cause) {
            super(cause);
        }
    }

    private Handler handler;
    private Map<String, Parser.Definition> apiDescription;

    public Processor(Handler handler, Map<String, Parser.Definition> apiDescription) {
        this.handler = handler;
        this.apiDescription = apiDescription;
    }

    public String process(String inputJson) {
        var result = _process(inputJson);
    }

    private record ProcessResult(String functionName, Map<String, Object> output) {}

    private ProcessResult _process(String functionInputJson) {
        var objectMapper = new ObjectMapper();
        JsonNode json;
        try {
            json = objectMapper.readTree(functionInputJson);
        } catch (JsonProcessingException e) {
            throw new InvalidJson(e);
        }

        List<Object> functionInput;
        try {
            functionInput = objectMapper.convertValue(json, new TypeReference<List<Object>>() {});
        } catch (IllegalArgumentException e) {
            throw new RuntimeException(e);
        }

        if (functionInput.size() != 3) {

        }

        var title = functionInput.get(0);

    }
}
