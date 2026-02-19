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
    sid?: string;
    rid?: string;
    subject?: string;
    reply?: string | null;
    timeout_ms?: number;
    data?: string;
    ok?: boolean;
    error?: string;
};

function encodeBytes(data: Uint8Array): string {
    return Buffer.from(data).toString("base64");
}

function decodeBytes(data: string): Uint8Array {
    return new Uint8Array(Buffer.from(data, "base64"));
}

export class Msg {
    public data: Uint8Array;
    public reply?: string;
    private connection: StdioNatsConnection;

    constructor(connection: StdioNatsConnection, data: Uint8Array, reply?: string) {
        this.connection = connection;
        this.data = data;
        this.reply = reply;
    }

    respond(data: Uint8Array) {
        if (!this.reply) {
            throw new Error("message has no reply subject");
        }
        this.connection.publish(this.reply, data);
    }
}

export class Subscription implements AsyncIterable<Msg> {
    private queue: Msg[] = [];
    private waiters: Array<(value: IteratorResult<Msg>) => void> = [];
    private closed = false;
    private connection: StdioNatsConnection;
    private sid: string;

    constructor(connection: StdioNatsConnection, sid: string) {
        this.connection = connection;
        this.sid = sid;
    }

    push(msg: Msg) {
        if (this.closed) {
            return;
        }

        if (this.waiters.length > 0) {
            const resolve = this.waiters.shift()!;
            resolve({ value: msg, done: false });
            return;
        }

        this.queue.push(msg);
    }

    async drain() {
        if (this.closed) {
            return;
        }
        this.closed = true;
        this.connection.unsubscribe(this.sid);
        while (this.waiters.length > 0) {
            const resolve = this.waiters.shift()!;
            resolve({ value: undefined as unknown as Msg, done: true });
        }
    }

    [Symbol.asyncIterator](): AsyncIterator<Msg> {
        return {
            next: async (): Promise<IteratorResult<Msg>> => {
                if (this.queue.length > 0) {
                    const msg = this.queue.shift()!;
                    return { value: msg, done: false };
                }
                if (this.closed) {
                    return { value: undefined as unknown as Msg, done: true };
                }

                return await new Promise<IteratorResult<Msg>>((resolve) => {
                    this.waiters.push(resolve);
                });
            },
        };
    }
}

class RequestResponse {
    data: Uint8Array;
    constructor(data: Uint8Array) {
        this.data = data;
    }
}

export class StdioNatsConnection {
    private sidCounter = 0;
    private ridCounter = 0;
    private subscriptions: Map<string, Subscription> = new Map();
    private pendingRequests: Map<string, { resolve: (v: RequestResponse) => void; reject: (e: Error) => void; timer: ReturnType<typeof setTimeout> | null }> = new Map();

    constructor() {
        const rl = readline.createInterface({
            input: process.stdin,
            crlfDelay: Infinity,
            terminal: false,
        });

        rl.on("line", (line) => {
            this.handleLine(line);
        });
    }

    request(subject: string, data: Uint8Array, options?: { timeout?: number }): Promise<RequestResponse> {
        const timeoutMs = Math.max(options?.timeout ?? 5000, 1);
        this.ridCounter += 1;
        const rid = `rid-${this.ridCounter}`;

        const promise = new Promise<RequestResponse>((resolve, reject) => {
            const timer = setTimeout(() => {
                this.pendingRequests.delete(rid);
                reject(new Error("request timed out"));
            }, timeoutMs);

            this.pendingRequests.set(rid, { resolve, reject, timer });
        });

        this.send({
            op: "request",
            rid,
            subject,
            timeout_ms: timeoutMs,
            data: encodeBytes(data),
        });

        return promise;
    }

    publish(subject: string, data: Uint8Array): void {
        this.send({
            op: "publish",
            subject,
            reply: null,
            data: encodeBytes(data),
        });
    }

    subscribe(subject: string): Subscription {
        this.sidCounter += 1;
        const sid = `sid-${this.sidCounter}`;
        const sub = new Subscription(this, sid);
        this.subscriptions.set(sid, sub);
        this.send({
            op: "subscribe",
            sid,
            subject,
        });
        return sub;
    }

    unsubscribe(sid: string): void {
        this.subscriptions.delete(sid);
        this.send({
            op: "unsubscribe",
            sid,
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

        if (frame.op === "message") {
            const sid = frame.sid;
            const data = frame.data;
            if (!sid || !data) {
                return;
            }
            const sub = this.subscriptions.get(sid);
            if (!sub) {
                return;
            }
            const msg = new Msg(this, decodeBytes(data), frame.reply ?? undefined);
            sub.push(msg);
            return;
        }

        if (frame.op === "request_result") {
            const rid = frame.rid;
            if (!rid) {
                return;
            }
            const pending = this.pendingRequests.get(rid);
            if (!pending) {
                return;
            }
            this.pendingRequests.delete(rid);
            if (pending.timer) {
                clearTimeout(pending.timer);
            }

            if (frame.ok) {
                pending.resolve(new RequestResponse(decodeBytes(frame.data ?? "")));
            } else {
                pending.reject(new Error(frame.error ?? "request failed"));
            }
            return;
        }
    }

    private send(frame: Frame) {
        const line = `${PROTO_PREFIX}${JSON.stringify(frame)}\n`;
        process.stdout.write(line);
    }
}

export type NatsConnection = StdioNatsConnection;

export async function connect(_options?: { servers?: string }): Promise<NatsConnection> {
    return new StdioNatsConnection();
}
