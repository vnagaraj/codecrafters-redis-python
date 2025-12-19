"""
Redis command parser for RESP protocol.

This module provides functionality to parse commands from the Redis Serialization Protocol (RESP).
It handles command extraction and validation for common Redis commands like PING and ECHO.
"""

from typing import List, Optional
import logging

logger: logging.Logger = logging.getLogger(__name__)


class RESPParser:
    """
    Parser for Redis Serialization Protocol (RESP) messages.
    
    Handles parsing of command data received from Redis clients and extracting
    the command name and arguments from the RESP format.
    """

    @staticmethod
    def parse_command(data: bytes) -> Optional[dict]:
        """
        Parse a RESP protocol command from bytes.
        
        Converts raw bytes from the network into a structured command dictionary
        containing the command name and its arguments.
        
        Args:
            data: Raw bytes received from the Redis client in RESP format.
                  Example: b"*1\r\n$4\r\nPING\r\n"
        
        Returns:
            A dictionary with keys:
            - 'command': str - The command name (e.g., 'PING', 'ECHO')
            - 'args': List[str] - The command arguments
            
            Returns None if the data cannot be parsed.
        
        Example:
            >>> data = b"*2\r\n$4\r\nECHO\r\n$5\r\nHello\r\n"
            >>> result = RESPParser.parse_command(data)
            >>> result['command']
            'ECHO'
            >>> result['args']
            ['Hello']
        """
        try:
            # Decode bytes to string
            decoded_data: str = data.decode('utf-8')
            
            # Split by RESP delimiter
            lines: List[str] = decoded_data.split('\r\n')
            
            if not lines or lines[0].startswith('*') is False:
                logger.warning(f"Invalid RESP format: {data}")
                return None
            
            # Parse the number of arguments
            num_args: int = int(lines[0][1:])  # Skip the '*' character
            
            # Extract command name (always at position 2)
            command_name: str = lines[2].upper()
            
            # Extract arguments
            args: List[str] = []
            # Arguments start at position 4 and follow the pattern:
            # $<length>\r\n<argument>\r\n
            for i in range(4, len(lines), 2):
                if i < len(lines) and lines[i]:
                    args.append(lines[i])
            
            return {
                'command': command_name,
                'args': args,
                'num_args': num_args
            }
        
        except (ValueError, IndexError, UnicodeDecodeError) as e:
            logger.error(f"Error parsing command: {e}")
            return None

    @staticmethod
    def get_command_name(parsed_command: dict) -> str:
        """
        Extract the command name from a parsed command dictionary.
        
        Args:
            parsed_command: Dictionary returned by parse_command()
        
        Returns:
            The command name as a string (e.g., 'PING', 'ECHO')
        """
        return parsed_command.get('command', '')

    @staticmethod
    def get_arguments(parsed_command: dict) -> List[str]:
        """
        Extract the arguments from a parsed command dictionary.
        
        Args:
            parsed_command: Dictionary returned by parse_command()
        
        Returns:
            List of command arguments
        """
        return parsed_command.get('args', [])

    @staticmethod
    def is_ping(parsed_command: Optional[dict]) -> bool:
        """
        Check if the parsed command is a PING command.
        
        Args:
            parsed_command: Dictionary returned by parse_command(), or None
        
        Returns:
            True if the command is PING, False otherwise
        """
        if parsed_command is None:
            return False
        return parsed_command.get('command') == 'PING'

    @staticmethod
    def is_echo(parsed_command: Optional[dict]) -> bool:
        """
        Check if the parsed command is an ECHO command.
        
        Args:
            parsed_command: Dictionary returned by parse_command(), or None
        
        Returns:
            True if the command is ECHO, False otherwise
        """
        if parsed_command is None:
            return False
        return parsed_command.get('command') == 'ECHO'

    @staticmethod
    def is_set(parsed_command: Optional[dict]) -> bool:
        """
        Check if the parsed command is a SET command.
        
        The SET command is used to store a value in Redis with an associated key.
        In RESP protocol, it follows the format:
        *3\r\n$3\r\nSET\r\n$<key_length>\r\n<key>\r\n$<value_length>\r\n<value>\r\n
        
        Args:
            parsed_command: Dictionary returned by parse_command(), or None
        
        Returns:
            True if the command is SET, False otherwise
        
        Example:
            >>> data = b"*3\r\n$3\r\nSET\r\n$4\r\nkey1\r\n$6\r\nvalue1\r\n"
            >>> cmd = RESPParser.parse_command(data)
            >>> RESPParser.is_set(cmd)
            True
            >>> cmd['args']
            ['key1', 'value1']
        
        Note:
            The SET command typically requires 2 arguments (key and value).
            Use get_arguments() to extract the key-value pair.
        """
        if parsed_command is None:
            return False
        return parsed_command.get('command') == 'SET'

    @staticmethod
    def is_get(parsed_command: Optional[dict]) -> bool:
        """
        Check if the parsed command is a GET command.
        
        The GET command is used to retrieve a value from Redis by its key.
        In RESP protocol, it follows the format:
        *2\r\n$3\r\nGET\r\n$<key_length>\r\n<key>\r\n
        
        Args:
            parsed_command: Dictionary returned by parse_command(), or None
        
        Returns:
            True if the command is GET, False otherwise
        
        Example:
            >>> data = b"*2\r\n$3\r\nGET\r\n$4\r\nkey1\r\n"
            >>> cmd = RESPParser.parse_command(data)
            >>> RESPParser.is_get(cmd)
            True
            >>> cmd['args']
            ['key1']
        
        Note:
            The GET command typically requires 1 argument (the key to retrieve).
            Use get_arguments() to extract the key.
        """
        if parsed_command is None:
            return False
        return parsed_command.get('command') == 'GET'

    @staticmethod
    def is_rpush(parsed_command: Optional[dict]) -> bool:
        """
        Check if the parsed command is an RPUSH command.
        
        The RPUSH command is used to append one or more values to the end of a list in Redis.
        In RESP protocol, it follows the format:
        *N\r\n$5\r\nRPUSH\r\n$<key_length>\r\n<key>\r\n$<value1_length>\r\n<value1>\r\n...$<valueN_length>\r\n<valueN>\r\n
        
        Args:
            parsed_command: Dictionary returned by parse_command(), or None
        
        Returns:
            True if the command is RPUSH, False otherwise
        
        Example:
            >>> data = b"*4\r\n$5\r\nRPUSH\r\n$4\r\nlist1\r\n$3\r\nval1\r\n$3\r\nval2\r\n"
            >>> cmd = RESPParser.parse_command(data)
            >>> RESPParser.is_rpush(cmd)
            True
            >>> cmd['args']
            ['list1', 'val1', 'val2']
        
        Note:
            The RPUSH command requires at least 2 arguments (the key and at least one value).
            Use get_arguments() to extract the key and values.
        """
        if parsed_command is None:
            return False
        return parsed_command.get('command') == 'RPUSH'

    @staticmethod
    def is_lrange(parsed_command: Optional[dict]) -> bool:
        """
        Check if the parsed command is an LRANGE command.
        
        The LRANGE command is used to retrieve a range of elements from a list in Redis.
        In RESP protocol, it follows the format:
        *4\r\n$6\r\nLRANGE\r\n$<key_length>\r\n<key>\r\n$<start_length>\r\n<start>\r\n$<stop_length>\r\n<stop>\r\n
        
        Args:
            parsed_command: Dictionary returned by parse_command(), or None
        
        Returns:
            True if the command is LRANGE, False otherwise
        
        Example:
            >>> data = b"*4\r\n$6\r\nLRANGE\r\n$4\r\nlist1\r\n$1\r\n0\r\n$2\r\n-1\r\n"
            >>> cmd = RESPParser.parse_command(data)
            >>> RESPParser.is_lrange(cmd)
            True
            >>> cmd['args']
            ['list1', '0', '-1']
        
        Note:
            The LRANGE command requires 3 arguments (the key, start index, and stop index).
            Use get_arguments() to extract these values.
        """
        if parsed_command is None:
            return False
        return parsed_command.get('command') == 'LRANGE'

    @staticmethod
    def is_lpush(parsed_command: Optional[dict]) -> bool:
        """
        Check if the parsed command is an LPUSH command.
        
        The LPUSH command is used to prepend one or more values to the beginning of a list in Redis.
        In RESP protocol, it follows the format:
        *N\r\n$5\r\nLPUSH\r\n$<key_length>\r\n<key>\r\n$<value1_length>\r\n<value1>\r\n...$<valueN_length>\r\n<valueN>\r\n
        
        Args:
            parsed_command: Dictionary returned by parse_command(), or None
        
        Returns:
            True if the command is LPUSH, False otherwise
        
        Example:
            >>> data = b"*4\r\n$5\r\nLPUSH\r\n$4\r\nlist1\r\n$3\r\nval1\r\n$3\r\nval2\r\n"
            >>> cmd = RESPParser.parse_command(data)
            >>> RESPParser.is_lpush(cmd)
            True
            >>> cmd['args']
            ['list1', 'val1', 'val2']
        
        Note:
            The LPUSH command requires at least 2 arguments (the key and at least one value).
            Use get_arguments() to extract the key and values.
        """
        if parsed_command is None:
            return False
        return parsed_command.get('command') == 'LPUSH'

    @staticmethod
    def is_llen(parsed_command: Optional[dict]) -> bool:
        """
        Check if the parsed command is an LLEN command.
        
        The LLEN command is used to get the length of a list stored in Redis.
        In RESP protocol, it follows the format:
        *2\r\n$4\r\nLLEN\r\n$<key_length>\r\n<key>\r\n
        
        Args:
            parsed_command: Dictionary returned by parse_command(), or None
        
        Returns:
            True if the command is LLEN, False otherwise
        
        Example:
            >>> data = b"*2\r\n$4\r\nLLEN\r\n$4\r\nlist1\r\n"
            >>> cmd = RESPParser.parse_command(data)
            >>> RESPParser.is_llen(cmd)
            True
            >>> cmd['args']
            ['list1']
        
        Note:
            The LLEN command requires 1 argument (the key of the list).
            Use get_arguments() to extract the key.
        """
        if parsed_command is None:
            return False
        return parsed_command.get('command') == 'LLEN'

    @staticmethod
    def is_lpop(self, parsed_command: Optional[dict]) -> bool:
        """
        Check if the parsed command is an LPOP command.
        
        The LPOP command is used to remove and return the first element of a list in Redis.
        In RESP protocol, it follows the format:
        *2\r\n$4\r\nLPOP\r\n$<key_length>\r\n<key>\r\n
        
        Args:
            parsed_command: Dictionary returned by parse_command(), or None
        
        Returns:
            True if the command is LPOP, False otherwise
        
        Example:
            >>> data = b"*2\r\n$4\r\nLPOP\r\n$4\r\nlist1\r\n"
            >>> cmd = RESPParser.parse_command(data)
            >>> RESPParser.is_lpop(cmd)
            True
            >>> cmd['args']
            ['list1']
        
        Note:
            The LPOP command requires 1 argument (the key of the list).
            Use get_arguments() to extract the key.
        """
        if parsed_command is None:
            return False
        return parsed_command.get('command') == 'LPOP'
