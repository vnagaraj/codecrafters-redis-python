import asyncio
import logging
import time
from typing import Tuple

from .parser import RESPParser
from .store import RedisStore

# Configuration constants
HOST: str = "localhost"
PORT: int = 6379
BUFFER_SIZE: int = 1024

# Protocol constants
PONG_RESPONSE: bytes = b"+PONG\r\n"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger: logging.Logger = logging.getLogger(__name__)

# Global Redis store instance
store: RedisStore = RedisStore()


def format_bulk_string_response(value: str) -> bytes:
    """
    Format a string value as a RESP Bulk String response.
    
    Args:
        value: The string value to format
    
    Returns:
        The RESP Bulk String encoded as bytes: $<length>\r\n<value>\r\n
    """
    value_bytes = value.encode('utf-8')
    value_length = str(len(value_bytes)).encode('utf-8')
    return b"$" + value_length + b"\r\n" + value_bytes + b"\r\n"

def format_integer_response(value: int) -> bytes:
    """
    Format an integer value as a RESP Integer response.
    
    Args:
        value: The integer value to format

    Returns:
        The RESP Integer encoded as bytes: :<value>\r\n
    """
    return f":{value}\r\n".encode('utf-8')


async def handle_client(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter
) -> None:
    """
    Handle a single client connection and respond to PING commands.
    
    This coroutine runs in a loop, continuously reading commands from the client
    and sending responses. It handles the Redis PING command in RESP protocol format.
    
    Args:
        reader: asyncio.StreamReader object for reading data from the client
        writer: asyncio.StreamWriter object for sending data to the client
    
    Returns:
        None
    
    Raises:
        Logs any exceptions that occur during client handling but doesn't raise them
    
    Example:
        This function is typically called automatically by asyncio.start_server():
        
        server = await asyncio.start_server(handle_client, HOST, PORT)
    """
    client_address: Tuple[str, int] = writer.get_extra_info('peername')
    logger.info(f"Client connected from {client_address}")
    
    try:
        while True:
            # Read up to BUFFER_SIZE bytes from the client
            # This call awaits until data arrives or connection closes
            data: bytes = await reader.read(BUFFER_SIZE)
            
            # Empty bytes means the client closed the connection
            if not data:
                logger.info(f"Client {client_address} disconnected")
                break

            logger.debug(f"Received data from {client_address}: {data}")
            
            # Parse the RESP command using the parser module
            parsed_command = RESPParser.parse_command(data)
            
            if parsed_command is None:
                logger.warning(f"Failed to parse command from {client_address}")
                continue
            
            # Handle PING command
            if RESPParser.is_ping(parsed_command):
                # Write PONG response to the output buffer
                writer.write(PONG_RESPONSE)
                
                # Flush the buffer and wait for data to be sent to client
                # This ensures the response is actually transmitted
                await writer.drain()
                logger.debug(f"Sent PONG to {client_address}")
            
            # Handle ECHO command
            elif RESPParser.is_echo(parsed_command):
                # Extract the message to echo back
                args = RESPParser.get_arguments(parsed_command)
                
                if not args:
                    logger.warning(f"ECHO command with no arguments from {client_address}")
                    continue
                
                message = args[0]  # First argument is the message
                message_bytes = message.encode('utf-8')
                message_length = str(len(message_bytes)).encode('utf-8')
                
                # Construct the RESP response for ECHO
                # Format: $<length>\r\n<message>\r\n
                echo_response = (
                    b"$" + message_length + b"\r\n" +
                    message_bytes + b"\r\n"
                )
                logger.debug(f"echo_response: {echo_response}")
                
                # Write ECHO response to the output buffer
                writer.write(echo_response)
                
                # Flush the buffer and wait for data to be sent to client
                await writer.drain()
                logger.debug(f"Sent ECHO to {client_address}: {message}")
            elif RESPParser.is_set(parsed_command):
                """Handle SET command - store a key-value pair"""
                args = RESPParser.get_arguments(parsed_command)

                if len(args) < 2:
                    logger.warning(f"SET command with insufficient arguments from {client_address}")
                    writer.write(b"-ERR SET requires key and value\r\n")
                    await writer.drain()
                    continue

                key = args[0]
                value = args[1]
                
                # Use RedisStore to set the value
                store.set(key, value)

                #now checking for expiry argument
                if len(args) > 2:
                    expiry_arg = args[2]
                    expiry_seconds = 0
                    if len(args) > 3:
                        time_unit = int(args[3])
                        try:
                            if expiry_arg.startswith("EX"):
                                expiry_seconds = time_unit
                            elif expiry_arg.startswith("PX"):
                                expiry_seconds = time_unit / 1000
                            else:   
                                raise ValueError("Invalid expiry argument")
                            store.set_expiry(key, expiry_seconds)
                            logger.debug(f"SET expiry for {key} to {expiry_seconds} seconds from {client_address}")
                        except (IndexError, ValueError):
                                logger.warning(f"Invalid expiry argument in SET command from {client_address}")
                                writer.write(b"-ERR Invalid expiry argument\r\n")
                                await writer.drain()
                                continue
                    else:
                        logger.warning(f"Expiry time missing in SET command from {client_address}")
                        writer.write(b"-ERR Expiry time missing\r\n")
                        await writer.drain()
                        continue
        
                
                # RESP Simple String response: +OK\r\n
                writer.write(b"+OK\r\n")
                await writer.drain()
                logger.debug(f"SET {key}={value} from {client_address}")
            
            elif RESPParser.is_get(parsed_command):
                """Handle GET command - retrieve a value by key"""
                args = RESPParser.get_arguments(parsed_command)

                if not args:
                    logger.warning(f"GET command with no arguments from {client_address}")
                    writer.write(b"-ERR GET requires a key\r\n")
                    await writer.drain()
                    continue

                key = args[0]
                
                # Use RedisStore to get the value
                value = store.get(key)

                
                if value is None:
                    # RESP Null Bulk String: $-1\r\n
                    get_response = b"$-1\r\n"
                elif key in store._expiry:
                    current_time = time.time()
                    if current_time >= store._expiry[key]:
                        # Key has expired
                        store.delete(key)
                        get_response = b"$-1\r\n"
                    else:
                        # Key exists and hasn't expired
                        get_response = format_bulk_string_response(value)
                else:
                    # Key exists with no expiration
                    get_response = format_bulk_string_response(value)
                
                # Write GET response to the output buffer
                writer.write(get_response)
                await writer.drain()
                logger.debug(f"GET {key} from {client_address}: {value}")

            elif RESPParser.is_rpush(parsed_command):
                """Handle RPUSH command - append values to a list"""
                args = RESPParser.get_arguments(parsed_command)

                if not args or len(args) < 2:
                    logger.warning(f"RPUSH command with insufficient arguments from {client_address}")
                    writer.write(b"-ERR RPUSH requires a key and at least one value\r\n")
                    await writer.drain()
                    continue

                key = args[0]
                values = args[1:]

                # Use RedisStore to append values to the list
                store.rpush(key, *values)

                logger.debug(f"values: {*values}")

                # Use RedisStore to get the values after push
                values = store.get(key)
                if values is None:  
                    # RESP Null Bulk String: $-1\r\n
                    rpush_response = b"$-1\r\n"
                else:
                    rpush_response = format_integer_response(values)

                # Write RPUSH response to the output buffer
                logger.debug(f"rpush_response: {rpush_response}")
                writer.write(rpush_response)
                await writer.drain()
                logger.debug(f"RPUSH {key}={values} from {client_address}")

            else:
                # Unknown command
                logger.warning(f"Unknown command from {client_address}: {parsed_command.get('command')}")
                
    except Exception as e:
        logger.error(f"Error handling client {client_address}: {e}")
    finally:
        # Ensure the connection is properly closed
        writer.close()
        await writer.wait_closed()


async def main() -> None:
    """
    Start the Redis server and run the event loop.
    
    This coroutine initializes an asyncio TCP server that listens for incoming
    client connections on the specified HOST and PORT. For each new client,
    it creates a concurrent task using the handle_client() coroutine.
    
    The server runs indefinitely until interrupted by a KeyboardInterrupt
    (Ctrl+C), at which point it gracefully shuts down.
    
    Returns:
        None
    
    Raises:
        KeyboardInterrupt: Caught internally and triggers graceful shutdown
    
    Note:
        This function should be run with asyncio.run(main())
    
    Example:
        if __name__ == "__main__":
            asyncio.run(main())
    """
    logger.info(f"Starting Redis server on {HOST}:{PORT}")
    
    # Create an async TCP server that accepts connections
    # asyncio.start_server() returns a Server object
    server: asyncio.Server = await asyncio.start_server(handle_client, HOST, PORT)
    
    try:
        # async with ensures proper cleanup when the server exits
        async with server:
            # serve_forever() runs the event loop indefinitely
            # It accepts new connections and handles them concurrently
            await server.serve_forever()
    except KeyboardInterrupt:
        # Graceful shutdown when user presses Ctrl+C
        logger.info("Server shutting down...")


if __name__ == "__main__":
    # asyncio.run() creates an event loop, runs main(), and closes the loop
    asyncio.run(main())
