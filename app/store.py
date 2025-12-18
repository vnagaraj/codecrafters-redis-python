"""
Redis in-memory key-value store with expiration support.

This module provides a simple, efficient key-value store implementation
for the Redis server with support for key expiration (TTL) using Python
dictionaries and __slots__ for memory efficiency.
"""

from typing import Optional
import logging
import time

logger: logging.Logger = logging.getLogger(__name__)


class RedisStore:
    """
    In-memory Redis key-value store with expiration support.
    
    Provides SET and GET operations with optional key expiration (TTL).
    Supports expiration management through dedicated methods for setting
    and checking TTL.
    
    Attributes:
        _data: Dictionary storing all key-value pairs
        _expiry: Dictionary storing expiration timestamps for keys with TTL
    """
    
    def __init__(self) -> None:
        """
        Initialize an empty Redis store with expiration support.
        
        Creates empty dictionaries for storing key-value pairs and their
        expiration timestamps.
        
        Example:
            >>> store = RedisStore()
            >>> store.set('key', 'value')
            >>> store.set_expiry('key', 60)  # Expires in 60 seconds
        """
        self._data: dict[str, str] = {}
        self._expiry: dict[str, float] = {}
    
    def set(self, key: str, value: str) -> None:
        """
        Store a value in the Redis store.
        
        This method stores a key-value pair. If the key already exists,
        its value is overwritten.
        
        Args:
            key: The key under which to store the value. Must be a string.
            value: The value to store. Must be a string.
        
        Returns:
            None
        
        Raises:
            TypeError: If key or value is not a string.
        
        Example:
            >>> store = RedisStore()
            >>> store.set('name', 'Alice')
            >>> store.set('age', '25')
        
        Time Complexity:
            O(1) average case
        """
        if not isinstance(key, str):
            raise TypeError(f"Key must be a string, got {type(key).__name__}")
        if not isinstance(value, str):
            raise TypeError(f"Value must be a string, got {type(value).__name__}")
        
        self._data[key] = value
        logger.debug(f"SET {key} = {value}")
    
    def get(self, key: str) -> Optional[str]:
        """
        Retrieve a value from the Redis store.
        
        This method retrieves the value associated with the given key.
        If the key does not exist, None is returned.
        
        Args:
            key: The key to look up. Must be a string.
        
        Returns:
            The value associated with the key, or None if the key doesn't exist.
        
        Raises:
            TypeError: If key is not a string.
        
        Example:
            >>> store = RedisStore()
            >>> store.set('name', 'Alice')
            >>> store.get('name')
            'Alice'
            >>> store.get('missing')
            None
        
        Time Complexity:
            O(1) average case
        """
        if not isinstance(key, str):
            raise TypeError(f"Key must be a string, got {type(key).__name__}")
        
        value = self._data.get(key)
        logger.debug(f"GET {key} = {value}")
        return value
    
    def delete(self, key: str) -> bool:
        """
        Delete a key-value pair from the Redis store.
        
        This method removes the given key and its associated value from the store.
        If the key doesn't exist, False is returned.
        
        Args:
            key: The key to delete. Must be a string.
        
        Returns:
            True if the key was deleted, False if the key didn't exist.
        
        Raises:
            TypeError: If key is not a string.
        
        Example:
            >>> store = RedisStore()
            >>> store.set('name', 'Alice')
            >>> store.delete('name')
            True
            >>> store.delete('name')
            False
        
        Time Complexity:
            O(1) average case
        """
        if not isinstance(key, str):
            raise TypeError(f"Key must be a string, got {type(key).__name__}")
        
        if key in self._data:
            del self._data[key]
            if key in self._expiry:
                del self._expiry[key]
            logger.debug(f"DEL {key}")
            return True

        logger.debug(f"DEL {key} - key not found")
        return False
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in the Redis store.
        
        This method checks whether the given key is present in the store.
        
        Args:
            key: The key to check. Must be a string.
        
        Returns:
            True if the key exists, False otherwise.
        
        Raises:
            TypeError: If key is not a string.
        
        Example:
            >>> store = RedisStore()
            >>> store.set('name', 'Alice')
            >>> store.exists('name')
            True
            >>> store.exists('missing')
            False
        
        Time Complexity:
            O(1) average case
        """
        if not isinstance(key, str):
            raise TypeError(f"Key must be a string, got {type(key).__name__}")
        
        exists = key in self._data
        logger.debug(f"EXISTS {key} = {exists}")
        return exists
    
    def keys(self) -> list[str]:
        """
        Get all keys currently stored in the Redis store.
        
        This method returns a list of all keys present in the store.
        
        Returns:
            A list of all keys in the store.
        
        Example:
            >>> store = RedisStore()
            >>> store.set('key1', 'value1')
            >>> store.set('key2', 'value2')
            >>> store.keys()
            ['key1', 'key2']
        
        Time Complexity:
            O(n) where n is the number of keys
        """
        return list(self._data.keys())
    
    def clear(self) -> None:
        """
        Clear all key-value pairs from the Redis store.
        
        This method removes all entries from the store, leaving it empty.
        
        Example:
            >>> store = RedisStore()
            >>> store.set('key', 'value')
            >>> store.clear()
            >>> store.get('key')
            None
        
        Time Complexity:
            O(n) where n is the number of keys
        """
        self._data.clear()
        logger.debug("FLUSHALL")
    
    def size(self) -> int:
        """
        Get the number of key-value pairs in the Redis store.
        
        This method returns the count of all entries currently stored.
        
        Returns:
            The number of keys in the store.
        
        Example:
            >>> store = RedisStore()
            >>> store.set('key1', 'value1')
            >>> store.set('key2', 'value2')
            >>> store.size()
            2
        
        Time Complexity:
            O(1)
        """
        return len(self._data)

    def set_expiry(self, key: str, seconds: float) -> None:
        """
        Set an expiration time on an existing key.
        
        This method sets a time-to-live (TTL) on a key, causing it to
        automatically expire after the specified duration. If the key
        doesn't exist, the expiration is still recorded for future use.
        
        Args:
            key: The key to set expiration on. Must be a string.
            seconds: The duration in seconds until the key expires. Must be
                    numeric and positive. Can be a float for subsecond precision.
        
        Returns:
            None
        
        Raises:
            TypeError: If key is not a string or seconds is not numeric.
            ValueError: If seconds is negative or zero.
        
        Example:
            >>> store = RedisStore()
            >>> store.set('temp', 'data')
            >>> store.set_expiry('temp', 30)  # Expires in 30 seconds
            >>> store.get('temp')
            'data'
        
        Time Complexity:
            O(1) average case
        """
        if not isinstance(key, str):
            raise TypeError(f"Key must be a string, got {type(key).__name__}")
        if not isinstance(seconds, (int, float)):
            raise TypeError(f"Seconds must be numeric, got {type(seconds).__name__}")
        if seconds <= 0:
            raise ValueError(f"Seconds must be positive, got {seconds}")
        
        current_time = time.time()
        self._expiry[key] = current_time + seconds
        logger.debug(f"EXPIRE {key} {seconds}s (expires at {self._expiry[key]})")

    def rpush(self, key: str, value: str) -> None:
        """
        Append a value to the list stored at key. If the key does not exist,
        it is created as an empty list before performing the push operation.
        
        Args:
            key: The key of the list. Must be a string.
            value: The value to append to the list. Must be a string.

        Returns:
            None

        Example:
            >>> store = RedisStore()
            >>> store.rpush('mylist', 'value1')
            >>> store.rpush('mylist', 'value2')
            >>> store.get('mylist')
            ['value1', 'value2']

        Time Complexity:
            O(1) average case
        """
        if not isinstance(key, str):
            raise TypeError(f"Key must be a string, got {type(key).__name__}")
        if not isinstance(value, str):
            raise TypeError(f"Value must be a string, got {type(value).__name__}")

        if key not in self._data:
            self._data[key] = []
        self._data[key].append(value)
        logger.debug(f"RPUSH {key} {value}")

    def lrange(self, key: str, start: int, end: int) -> list[str] | None:       
        """
        Retrieve a range of elements from the list stored at key.
        
        Args:
            key: The key of the list. Must be a string.
            start: The starting index of the range (inclusive).
            end: The ending index of the range (inclusive). -1 means the last element.      

        Returns:
            A list of elements in the specified range, or None if the key does not exist.
        """
        if key not in self._data:
            return None
        return self._data[key][start:end + 1]   