cases = {
    'auth': [
        [[{'Ok': {}}, {'fn.test': {}}], [{}, {'Ok': {}}]],
        [[{'result': {'_ErrorUnauthenticated': {'message!': 'a'}}}, {'fn.test': {}}], [{}, {'_ErrorUnauthenticated': {'message!': 'a'}}]],
        [[{'result': {'_ErrorUnauthorized': {'message!': 'a'}}}, {'fn.test': {}}], [{}, {'_ErrorUnauthorized': {'message!': 'a'}}]],
   ]
}