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

export function encodeBase64(uint8Array: Uint8Array): string {
    if (typeof window !== 'undefined') {
      // Browser environment
      return btoa(String.fromCharCode(...uint8Array));
    } else {
      // Node.js environment
      return Buffer.from(uint8Array).toString('base64');
    }
}
  
export function decodeBase64(base64String: string): Uint8Array {
    if (typeof window !== 'undefined') {
      // Browser environment
      return Uint8Array.from(atob(base64String), c => c.charCodeAt(0));
    } else {
      // Node.js environment
      return Uint8Array.from(Buffer.from(base64String, 'base64'));
    }
}