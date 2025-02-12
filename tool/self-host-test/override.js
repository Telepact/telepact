console.log('overriding!!!!');

window.getAuthHeader = function() {
    return {
        'token': 'secret-1234'
    };
}