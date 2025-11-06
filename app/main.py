import asyncio

async def handle_client(reader, writer):
    """Handles one client connection using asyncio streams."""
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break  # client closed connection
            writer.write(b"+PONG\r\n")
            await writer.drain()  # flush buffer
    except ConnectionResetError:
        pass
    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    print("Logs from your program will appear here!")

    server = await asyncio.start_server(
        handle_client, host="localhost", port=6379
    )

    # Show the listening address
    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on {addrs}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
