package io.github.brenbar.uapi;

import java.util.List;

/**
 * The strategy used by the client to maintain binary encodings compatible with
 * the server.
 */
public interface ClientBinaryStrategy {

    /**
     * Update the strategy according to a recent binary encoding checksum returned
     * by the server.
     * 
     * @param checksum
     */
    void update(Integer checksum);

    /**
     * Get the current binary encoding strategy as a list of binary encoding
     * checksums that should be sent to the server.
     * 
     * @return
     */
    List<Integer> getCurrentChecksums();
}
