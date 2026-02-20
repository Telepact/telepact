//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

import * as readline from "node:readline";

const PROTO_PREFIX = "@@TPSTDIO@@";

type Frame = {
    op: string;
    lid?: string;
    cid?: string;
    channel?: string;
    reply_channel?: string | null;
    timeout_ms?: number;
    payload?: string;
    ok?: boolean;
    error?: string;
};

function encodeBytes(data: Uint8Array): string {
    return Buffer.from(data).toString("base64");
}

function decodeBytes(data: string): Uint8Array {
    return new Uint8Array(Buffer.from(data, "base64"));
}

export class TransportMessage {
    public payload: Uint8Array;
    public replyChannel?: string;
    private transport: StdioTransport;

    constructor(transport: StdioTransport, payload: Uint8Array, replyChannel?: string) {
        this.transport = transport;
        this.payload = payload;
        this.replyChannel = replyChannel;
    }

    respond(payload: Uint8Array) {
        if (!this.replyChannel) {
            throw new Error("message has no reply channel");
        }
        this.transport.send(this.replyChannel, payload);
    }
}

export class Listener implements AsyncIterable<TransportMessage> {
    private queue: TransportMessage[] = [];
    private waiters: Array<(value: IteratorResult<TransportMessage>) => void> = [];
    private closed = false;
    private transport: StdioTransport;
    private lid: string;

    constructor(transport: StdioTransport, lid: string) {
        this.transport = transport;
        this.lid = lid;
    }

    push(message: TransportMessage) {
        if (this.closed) {
            return;
        }

        if (this.waiters.length > 0) {
            const resolve = this.waiters.shift()!;
            resolve({ value: message, done: false });
            return;
        }

        this.queue.push(message);
    }

    async close(_limit?: number) {
        if (this.closed) {
            return;
        }
        this.closed = true;
        this.transport.unlisten(this.lid);
        while (this.waiters.length > 0) {
            const resolve = this.waiters.shift()!;
            resolve({ value: undefined as unknown as TransportMessage, done: true });
        }
    }

    [Symbol.asyncIterator](): AsyncIterator<TransportMessage> {
        return {
            next: async (): Promise<IteratorResult<TransportMessage>> => {
                if (this.queue.length > 0) {
                    const message = this.queue.shift()!;
                    return { value: message, done: false };
                }
                if (this.closed) {
                    return { value: undefined as unknown as TransportMessage, done: true };
                }

                return await new Promise<IteratorResult<TransportMessage>>((resolve) => {
                    this.waiters.push(resolve);
                });
            },
        };
    }
}

export class CallResult {
    payload: Uint8Array;
    constructor(payload: Uint8Array) {
        this.payload = payload;
    }
}

export class StdioTransport {
    private lidCounter = 0;
    private cidCounter = 0;
    private listeners: Map<string, Listener> = new Map();
    private pendingCalls: Map<string, {
        resolve: (value: CallResult) => void;
        reject: (error: Error) => void;
        timer: ReturnType<typeof setTimeout> | null;
    }> = new Map();

    constructor() {
        const rl = readline.createInterface({
            input: process.stdin,
            crlfDelay: Infinity,
            terminal: false,
        });

        rl.on("line", (line: string) => {
            this.handleLine(line);
        });
    }

    call(channel: string, payload: Uint8Array, options?: { timeout?: number }): Promise<CallResult> {
        const timeoutMs = Math.max(options?.timeout ?? 5000, 1);
        this.cidCounter += 1;
        const cid = `cid-${this.cidCounter}`;

        const promise = new Promise<CallResult>((resolve, reject) => {
            const timer = setTimeout(() => {
                this.pendingCalls.delete(cid);
                reject(new Error("call timed out"));
            }, timeoutMs);

            this.pendingCalls.set(cid, { resolve, reject, timer });
        });

        this.sendFrame({
            op: "call",
            cid,
            channel,
            timeout_ms: timeoutMs,
            payload: encodeBytes(payload),
        });

        return promise;
    }

    send(channel: string, payload: Uint8Array): void {
        this.sendFrame({
            op: "send",
            channel,
            reply_channel: null,
            payload: encodeBytes(payload),
        });
    }

    listen(channel: string): Listener {
        this.lidCounter += 1;
        const lid = `lid-${this.lidCounter}`;
        const listener = new Listener(this, lid);
        this.listeners.set(lid, listener);
        this.sendFrame({
            op: "listen",
            lid,
            channel,
        });
        return listener;
    }

    unlisten(lid: string): void {
        this.listeners.delete(lid);
        this.sendFrame({
            op: "unlisten",
            lid,
        });
    }

    private handleLine(line: string) {
        if (!line.startsWith(PROTO_PREFIX)) {
            return;
        }

        let frame: Frame;
        try {
            frame = JSON.parse(line.slice(PROTO_PREFIX.length));
        } catch {
            return;
        }

        if (frame.op === "event") {
            const lid = frame.lid;
            const payloadB64 = frame.payload;
            if (!lid || !payloadB64) {
                return;
            }
            const listener = this.listeners.get(lid);
            if (!listener) {
                return;
            }
            const message = new TransportMessage(
                this,
                decodeBytes(payloadB64),
                (frame.reply_channel ?? undefined) || undefined,
            );
            listener.push(message);
            return;
        }

        if (frame.op === "call_result") {
            const cid = frame.cid;
            if (!cid) {
                return;
            }
            const pending = this.pendingCalls.get(cid);
            if (!pending) {
                return;
            }
            this.pendingCalls.delete(cid);
            if (pending.timer) {
                clearTimeout(pending.timer);
            }

            if (frame.ok) {
                const payloadB64 = frame.payload ?? "";
                pending.resolve(new CallResult(decodeBytes(payloadB64)));
            } else {
                pending.reject(new Error(frame.error ?? "call failed"));
            }
            return;
        }
    }

    private sendFrame(frame: Frame) {
        const line = `${PROTO_PREFIX}${JSON.stringify(frame)}\n`;
        process.stdout.write(line);
    }
}

export async function openTransport(_options?: { endpoint?: string }): Promise<StdioTransport> {
    return new StdioTransport();
}
