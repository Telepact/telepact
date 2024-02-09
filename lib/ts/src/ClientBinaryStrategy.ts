/**
 * The strategy used by the client to maintain binary encodings compatible with
 * the server.
 */
export interface ClientBinaryStrategy {
    /**
     * Update the strategy according to a recent binary encoding checksum returned
     * by the server.
     * 
     * @param checksum
     */
    update(checksum: number): void;

    /**
     * Get the current binary encoding strategy as a list of binary encoding
     * checksums that should be sent to the server.
     * 
     * @return
     */
    getCurrentChecksums(): number[];
}
