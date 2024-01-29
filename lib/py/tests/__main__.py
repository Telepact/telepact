import asyncio
import tests.test_server

print("Starting", flush=True)
asyncio.run(tests.test_server.run_dispatcher_server())
print("Exiting", flush=True)
