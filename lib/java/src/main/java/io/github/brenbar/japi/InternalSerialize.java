package io.github.brenbar.japi;

import java.util.Deque;
import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.Objects;
import java.util.Optional;
import java.util.stream.Collectors;

class InternalSerialize {

    static List<Object> serverBinaryEncode(List<Object> message, BinaryEncoder binaryEncoder) {
        var headers = (Map<String, Object>) message.get(1);

        var clientKnownChecksums = (List<Long>) headers.remove("_clientKnownBinaryChecksums");
        if (clientKnownChecksums == null || !clientKnownChecksums.contains(binaryEncoder.checksum)) {
            headers.put("_binaryEncoding", binaryEncoder.encodeMap);
        }

        return binaryEncoder.encode(message);
    }

    static List<Object> serverBinaryDecode(List<Object> message, BinaryEncoder binaryEncoder)
            throws BinaryEncoderUnavailableError {
        var headers = (Map<String, Object>) message.get(1);

        var binaryChecksums = (List<Long>) headers.get("_bin");
        headers.put("_clientKnownBinaryChecksums", binaryChecksums);

        var binaryChecksum = binaryChecksums.get(0);

        if (!Objects.equals(binaryChecksum, binaryEncoder.checksum)) {
            throw new BinaryEncoderUnavailableError();
        }

        return binaryEncoder.decode(message);
    }

    static List<Object> clientBinaryEncode(List<Object> message, Deque<BinaryEncoder> recentBinaryEncoders)
            throws BinaryEncoderUnavailableError {
        var headers = (Map<String, Object>) message.get(1);

        var checksums = recentBinaryEncoders.stream().map(be -> be.checksum).toList();
        headers.put("_bin", checksums);

        BinaryEncoder binaryEncoder;
        try {
            binaryEncoder = recentBinaryEncoders.getFirst();
        } catch (NoSuchElementException e) {
            throw new BinaryEncoderUnavailableError();
        }

        return binaryEncoder.encode(message);
    }

    static List<Object> clientBinaryDecode(List<Object> message, Deque<BinaryEncoder> recentBinaryEncoders)
            throws BinaryEncoderUnavailableError {
        var headers = (Map<String, Object>) message.get(1);

        var binaryChecksums = (List<Long>) headers.get("_bin");
        var binaryChecksum = binaryChecksums.get(0);

        // If there is a binary encoding included on this message, cache it
        if (headers.containsKey("_binaryEncoding")) {
            var initialBinaryEncoding = (Map<String, Object>) headers.get("_binaryEncoding");
            // Ensure everything is a long
            var binaryEncoding = initialBinaryEncoding.entrySet().stream()
                    .collect(Collectors.toMap(e -> e.getKey(), e -> {
                        var value = e.getValue();
                        if (value instanceof Integer i) {
                            return Long.valueOf(i);
                        } else if (value instanceof Long l) {
                            return l;
                        } else {
                            throw new RuntimeException("Unexpected type");
                        }
                    }));
            var newBinaryEncoder = new BinaryEncoder(binaryEncoding, binaryChecksum);
            recentBinaryEncoders.add(newBinaryEncoder);

            // We need to maintain 2 binary encodings in case a server is undergoing an API
            // change during a new jAPI deployment
            if (recentBinaryEncoders.size() >= 3) {
                recentBinaryEncoders.removeLast();
            }
        }

        var binaryEncoder = findBinaryEncoder(recentBinaryEncoders, binaryChecksum);
        if (!binaryEncoder.isPresent()) {
            throw new BinaryEncoderUnavailableError();
        }

        return binaryEncoder.get().decode(message);
    }

    private static Optional<BinaryEncoder> findBinaryEncoder(Deque<BinaryEncoder> binaryEncoderStore, Long checksum) {
        for (var binaryEncoder : binaryEncoderStore) {
            if (Objects.equals(binaryEncoder.checksum, checksum)) {
                return Optional.of(binaryEncoder);
            }
        }
        return Optional.empty();
    }

}
