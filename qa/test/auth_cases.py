cases = {
    'auth': [
        [[{'Ok': {}}, {'fn.test': {}}], [{}, {'Ok': {}}]],
        [[{'result': {'ErrorUnauthenticated_': {'message!': 'a'}}}, {'fn.test': {}}], [{}, {'ErrorUnauthenticated_': {'message!': 'a'}}]],
        [[{'result': {'ErrorUnauthorized_': {'message!': 'a'}}}, {'fn.test': {}}], [{}, {'ErrorUnauthorized_': {'message!': 'a'}}]],
   ]
}