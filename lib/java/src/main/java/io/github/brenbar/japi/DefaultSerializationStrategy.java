package io.github.brenbar.japi;

import java.io.IOException;
import java.util.List;

import org.msgpack.jackson.dataformat.MessagePackFactory;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

class DefaultSerializationStrategy implements SerializationStrategy {

    private ObjectMapper jsonMapper = new ObjectMapper();
    private ObjectMapper binaryMapper = new ObjectMapper(new MessagePackFactory());

    @Override
    public byte[] toJson(List<Object> japiMessage) {
        try {
            return jsonMapper.writeValueAsBytes(japiMessage);
        } catch (JsonProcessingException e) {
            throw new SerializationError(e);
        }
    }

    public byte[] toMsgPack(List<Object> japiMessage) {
        try {
            return binaryMapper.writeValueAsBytes(japiMessage);
        } catch (JsonProcessingException e) {
            throw new SerializationError(e);
        }
    }

    @Override
    public List<Object> fromJson(byte[] bytes) throws DeserializationError {
        try {
            return jsonMapper.readValue(bytes, new TypeReference<List<Object>>() {
            });
        } catch (IOException e) {
            throw new DeserializationError(e);
        }
    }

    @Override
    public List<Object> fromMsgPack(byte[] bytes) throws DeserializationError {
        try {
            return binaryMapper.readValue(bytes, new TypeReference<List<Object>>() {
            });
        } catch (IOException e) {
            throw new DeserializationError(e);
        }
    }

}