package io.github.brenbar.japi;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.msgpack.jackson.dataformat.MessagePackFactory;

import java.io.IOException;
import java.util.List;

public interface Serializer {

    public static class SerializationError extends RuntimeException {
        public SerializationError(Throwable cause) {
            super(cause);
        }
    }
    public static class DeserializationError extends Exception {
        public DeserializationError(Throwable cause) {
            super(cause);
        }
    }


    byte[] serializeToJson(List<Object> japiMessage);
    byte[] serializeToMsgPack(List<Object> japiMessage);
    List<Object> deserializeFromJson(byte[] bytes) throws DeserializationError;
    List<Object> deserializeFromMsgPack(byte[] bytes) throws DeserializationError;

    public static class Default implements Serializer {

        private ObjectMapper jsonMapper = new ObjectMapper();
        private ObjectMapper binaryMapper = new ObjectMapper(new MessagePackFactory());

        @Override
        public byte[] serializeToJson(List<Object> japiMessage) {
            try {
                return jsonMapper.writeValueAsBytes(japiMessage);
            } catch (JsonProcessingException e) {
                throw new SerializationError(e);
            }
        }

        public byte[] serializeToMsgPack(List<Object> japiMessage) {
            try {
                return binaryMapper.writeValueAsBytes(japiMessage);
            } catch (JsonProcessingException e) {
                throw new SerializationError(e);
            }
        }

        @Override
        public List<Object> deserializeFromJson(byte[] bytes) throws DeserializationError {
            try {
                return jsonMapper.readValue(bytes, new TypeReference<List<Object>>() {});
            } catch (IOException e) {
                throw new DeserializationError(e);
            }
        }

        @Override
        public List<Object> deserializeFromMsgPack(byte[] bytes) throws DeserializationError {
            try {
                return binaryMapper.readValue(bytes, new TypeReference<List<Object>>() {});
            } catch (IOException e) {
                throw new DeserializationError(e);
            }
        }

    }
}
