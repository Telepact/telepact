from telepact import Message, Server, TelepactSchema

schema = TelepactSchema.from_directory('./api')

async def divide(function_name: str, request_message: Message) -> Message:
    args = request_message.body[function_name]
    x, y = args['x'], args['y']
    if y == 0:
        return Message({}, {'ErrorCannotDivideByZero': {}})
    return Message({}, {'Ok_': {'result': x / y}})

options = Server.Options()
options.auth_required = False
server = Server(schema, {'fn.divide': divide}, options)

# Plug into any framework — Starlette, Flask, FastAPI...
async def http_handler(request):
    response = await server.process(await request.body())
    return Response(content=response.bytes)
