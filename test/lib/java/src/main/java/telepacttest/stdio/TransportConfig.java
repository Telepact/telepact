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

public class TransportConfig {
    public final String endpoint;

    public TransportConfig(String endpoint) {
        this.endpoint = endpoint;
    }

    public static class Builder {
        private String endpoint;

        public Builder endpoint(String endpoint) {
            this.endpoint = endpoint;
            return this;
        }

        public TransportConfig build() {
            return new TransportConfig(this.endpoint);
        }
    }
}
