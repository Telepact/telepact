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

package telepacttest.stdio;

public class TransportMessage {
    private final byte[] payload;
    private final String replyChannel;
    private final Transport transport;

    public TransportMessage(Transport transport, byte[] payload, String replyChannel) {
        this.transport = transport;
        this.payload = payload;
        this.replyChannel = replyChannel;
    }

    public byte[] getPayload() {
        return payload;
    }

    public String getReplyChannel() {
        return replyChannel;
    }

    public void respond(byte[] payload) {
        if (replyChannel == null) {
            throw new RuntimeException("message has no reply channel");
        }
        transport.send(replyChannel, payload);
    }
}
