"""
Redis in-memory key-value store.

This module provides a simple, efficient key-value store implementation
for the Redis server using a Python dictionary.
"""

from typing import Optional
import logging

logger: logging.Logger = logging.getLogger(__name__)


class RedisStore:
    """
    Simple in-memory Redis key-value store.
    
    Provides basic SET and GET operations with memory-efficient storage
    using __slots__ to reduce memory overhead.
    
    Attributes:
        _data: Internal dictionary storing all key-value pairs
    """
    
    __slots__ = ('_data',)
    
    def __init__(self) -> None:
        """
        Initialize an empty Redis store.
        
        Example:
            >>> store = RedisStore()
            >>> store.set('key', 'value')
        """
        self._data: dict[str, str] = {}
    
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
