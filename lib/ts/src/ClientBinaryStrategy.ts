export abstract class ClientBinaryStrategy {
    /**
     * The strategy used by the client to maintain binary encodings compatible with
     * the server.
     */

    public abstract updateChecksum(checksum: number): void;
    /**
     * Update the strategy according to a recent binary encoding checksum returned
     * by the server.
     *
     * @param checksum - The checksum returned by the server.
     */

    public abstract getCurrentChecksums(): number[];
    /**
     * Get the current binary encoding strategy as a list of binary encoding
     * checksums that should be sent to the server.
     *
     * @returns A list of checksums.
     */
}
