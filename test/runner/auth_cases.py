cases = {
    'auth': [
        [[{'Ok_': {}}, {'fn.test': {}}], [{}, {'Ok_': {}}]],
        [[{'result': {'ErrorUnauthenticated_': {'message!': 'a'}}}, {'fn.test': {}}], [{}, {'ErrorUnauthenticated_': {'message!': 'a'}}]],
        [[{'result': {'ErrorUnauthorized_': {'message!': 'a'}}}, {'fn.test': {}}], [{}, {'ErrorUnauthorized_': {'message!': 'a'}}]],
   ]
}