//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

console.log('overriding!!!!');

window.getAuthHeader = function() {
    return {
        'token': 'secret-1234'
    };
}