import { Client, ClientOptions, Server, ServerOptions, Message, SerializationError, Serializer } from 'uapi'
import { NatsConnection, connect, StringCodec, Msg, Subscription } from 'nats'
import fs from 'fs'
import { min, max, mean, median, quantile } from 'simple-statistics'

class Timer {
    public values: number[] = [];

    public startTimer(): () => void {
        const start = performance.now();
        return () => {
            const end = performance.now();
            this.values.push(end - start);
        }
    }
}

class Registry {
    public timers: Record<string, Timer> = {}

    public register(name: string, timer: Timer) {
        this.timers[name] = timer;
    }

    public report() {
        for (const [name, timer] of Object.entries(this.timers)) {
            const fileName = `./metrics/${name}.csv`;

            if (!fs.existsSync(fileName)) {
                fs.mkdirSync('./metrics');

                const header = 'count,min,max,mean,median,p75,p95,p99\n';
                fs.writeFileSync(fileName, header);
            }

            const v = timer.values;
            const row = `${v.length},${min(v)},${max(v)},${mean(v)},${median(v)},${quantile(v, 0.75)},${quantile(v, 0.95)},${quantile(v, 0.99)}\n`
            
            fs.writeFileSync(fileName, row);
        }
    }
}

function startClientTestServer(
    connection: NatsConnection,
    registry: Registry,
    clientFrontdoorTopic: string,
    clientBackdoorTopic: string,
    defaultBinary: boolean
): void {
    const timer = new Timer();
    registry.register(clientBackdoorTopic, timer);

    const adapter: (m: Message, s: Serializer) => Promise<Message> = async (m, s) => {
        try {
            let requestBytes: Uint8Array;
            try {
                requestBytes = s.serialize(m);
            } catch (e) {
                if (e instanceof SerializationError) {
                    return new Message({ "numberTooBig": true }, { "_ErrorUnknown": {} });
                } else {
                    throw e;
                }
            }

            console.log(`   <-c  ${new TextDecoder().decode(requestBytes)}`);
            const natsResponseMessage = await connection.request(clientBackdoorTopic, requestBytes, { timeout: 5000 });
            const responseBytes = natsResponseMessage.data;

            console.log(`   ->c  ${new TextDecoder().decode(responseBytes)}`);

            const responseMessage = s.deserialize(responseBytes);
            return responseMessage;
        } catch (e) {
            console.error(e);
            throw e;
        }
    };

    const options = new ClientOptions();
    options.useBinary = defaultBinary;
    const client = new Client(adapter, options);

    const sub = connection.subscribe(clientFrontdoorTopic);
    
    (async (s: Subscription) => {
        for await (const msg of s) {
            const requestBytes = msg.data;
            const requestJson = new TextDecoder().decode(requestBytes);
    
            console.log(`   ->C  ${requestJson}`);
    
            const requestPseudoJson = JSON.parse(requestJson);
            const requestHeaders = requestPseudoJson[0] as Map<string, any>;
            const requestBody = requestPseudoJson[1] as Map<string, any>;
            const request = new Message(requestHeaders, requestBody);
    
            let response: Message;
            const time = timer.startTimer();
            try {
                response = await client.request(request);
            } finally {
                time();
            }
    
            const responsePseudoJson = [response.header, response.body];

            const responseJson = JSON.stringify(responsePseudoJson);
    
            const responseBytes = new TextEncoder().encode(responseJson);
    
            console.log(`   <-C  ${new TextDecoder().decode(responseBytes)}`);
    
            connection.publish(msg.reply!, responseBytes);
        }
    })(sub);
}