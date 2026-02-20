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

import java.time.Duration;

public interface Transport extends AutoCloseable {
    CallResult call(String channel, byte[] payload, Duration timeout) throws InterruptedException;

    void send(String channel, byte[] payload);

    TransportListener openListener(TransportHandler handler);

    @Override
    void close();
}
