import { ClientBinaryStrategy } from './ClientBinaryStrategy';

export class Checksum {
    constructor(
        public value: number,
        public expiration: number,
    ) {}
}

export class DefaultClientBinaryStrategy implements ClientBinaryStrategy {
    private primary: Checksum | null = null;
    private secondary: Checksum | null = null;
    private lastUpdate: Date = new Date();

    updateChecksum(newChecksum: number): void {
        if (!this.primary) {
            this.primary = new Checksum(newChecksum, 0);
            return;
        }

        if (this.primary.value !== newChecksum) {
            this.secondary = this.primary;
            this.primary = new Checksum(newChecksum, 0);
            if (this.secondary) {
                this.secondary.expiration += 1;
            }
            return;
        }

        this.lastUpdate = new Date();
    }

    getCurrentChecksums(): number[] {
        if (!this.primary) {
            return [];
        } else if (!this.secondary) {
            return [this.primary.value];
        } else {
            const minutesSinceLastUpdate = (Date.now() - this.lastUpdate.getTime()) / (1000 * 60);

            // Every 10 minute interval of non-use is a penalty point
            const penalty = Math.floor(minutesSinceLastUpdate / 10) + 1;

            if (this.secondary) {
                this.secondary.expiration += 1 * penalty;
            }

            if (this.secondary && this.secondary.expiration > 5) {
                this.secondary = null;
                return [this.primary.value];
            } else {
                return [this.primary.value, this.secondary.value];
            }
        }
    }
}
