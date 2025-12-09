import socket
import logging

# Configuration constants
HOST = "localhost"
PORT = 6379
BUFFER_SIZE = 1024

# Protocol constants
PING_COMMAND = b"PING"
PONG_RESPONSE = b"+PONG\r\n"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handle_client(connection, client_address):
    """Handle a single client connection and respond to commands."""
    logger.info(f"Client connected from {client_address}")
    try:
        while True:
            data = connection.recv(BUFFER_SIZE)
            if not data:
                logger.info(f"Client {client_address} disconnected")
                break
            
            # Parse and respond to PING command
            if PING_COMMAND in data.upper():
                connection.sendall(PONG_RESPONSE)
                logger.debug(f"Sent PONG to {client_address}")
    except Exception as e:
        logger.error(f"Error handling client {client_address}: {e}")
    finally:
        connection.close()


def main():
    """Start the Redis server and accept client connections."""
    logger.info(f"Starting Redis server on {HOST}:{PORT}")
    
    server_socket = socket.create_server((HOST, PORT), reuse_port=True)
    try:
        while True:
            connection, client_address = server_socket.accept()
            handle_client(connection, client_address)
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
