#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

cases = {
    'auth': [
        [[{'@ok_': {}}, {'fn.test': {}}], [{}, {'Ok_': {}}]],
        [[{'@result': {'ErrorUnauthenticated_': {'message!': 'a'}}}, {'fn.test': {}}], [{}, {'ErrorUnauthenticated_': {'message!': 'a'}}]],
        [[{'@result': {'ErrorUnauthorized_': {'message!': 'a'}}}, {'fn.test': {}}], [{}, {'ErrorUnauthorized_': {'message!': 'a'}}]],
        [[{}, {'fn.api_': {}}], [{}, {'Ok_': {'api': [{'info.AuthExample': {}}, {'///': ' A standard error. ', 'errors.Auth_': [{'///': ' The credentials in the `_auth` header were missing or invalid. ', 'ErrorUnauthenticated_': {'message!': 'string'}}, {'///': ' The credentials in the `_auth` header were insufficient to run the function. ', 'ErrorUnauthorized_': {'message!': 'string'}}]}, {'fn.test': {}, '->': [{'Ok_': {}}]}, {'///': [' The `@auth_` header is the conventional location for sending credentials to     ', ' the server for the purpose of authentication and authorization.                 '], 'headers.Auth_': {'@auth_': 'struct.Auth_'}, '->': {}}, {'struct.Auth_': {'token': 'string'}}]}}]]
   ]
}