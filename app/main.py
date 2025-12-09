import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    while True:
        connection, client_address = server_socket.accept()  # wait for client
        try:
            # Keep the connection open and handle multiple commands
            while True:
                data = connection.recv(1024)
                if not data:
                    # Client closed the connection
                    break
                
                # Check if PING command is in the received data
                if b"PING" in data.upper():
                    connection.sendall(b"+PONG\r\n")
        finally:
            connection.close()


if __name__ == "__main__":
    main()
