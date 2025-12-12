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
        if parsed_command is None:
            return False
        return parsed_command.get('command') == 'SET'

    @staticmethod
    def is_get(parsed_command: Optional[dict]) -> bool:
        if parsed_command is None:
            return False
        return parsed_command.get('command') == 'GET'
