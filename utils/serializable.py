"""
Provides serialization capabilities for game components.
"""
import json
from pathlib import Path
from typing import Any, TextIO, Union

from game.types import FilePath


class SerializationError(Exception):
    """Base exception for serialization-related errors."""
    pass


class FileOperationError(SerializationError):
    """Raised when file operations fail."""
    pass


class JSONSerializationError(SerializationError):
    """Raised when JSON serialization/deserialization fails."""
    pass


class Serializable:
    """Base class for objects that can be serialized to and from JSON files.
    
    This class provides a consistent interface for saving and loading object
    state to/from JSON files, with proper error handling and resource management.
    
    Attributes:
        data: The data to be serialized/deserialized
    """
    
    def __init__(self) -> None:
        """Initialize a new Serializable instance."""
        self.data: Any = None
    
    def serialize(self, path: FilePath, mode: str) -> TextIO:
        """Open a file for serialization with proper error handling.
        
        Args:
            path: Path to the file to open
            mode: File open mode ('r', 'w', etc.)
            
        Returns:
            An open file handle
            
        Raises:
            FileOperationError: If the file cannot be opened
        """
        try:
            return open(Path(path), mode, encoding='utf-8')
        except (OSError, IOError) as e:
            raise FileOperationError(f"Failed to open file {path}: {str(e)}") from e
    
    def write(self, path: FilePath) -> None:
        """Write the object's data to a JSON file.
        
        Args:
            path: Path where the file should be written
            
        Raises:
            FileOperationError: If the file cannot be written
            JSONSerializationError: If the data cannot be serialized to JSON
        """
        try:
            with self.serialize(path, 'w') as file:
                json.dump(self.data, file, indent=4)
        except json.JSONEncodeError as e:
            raise JSONSerializationError(f"Failed to serialize data to JSON: {str(e)}") from e
    
    def load(self, path: FilePath) -> Any:
        """Load data from a JSON file.
        
        Args:
            path: Path to the JSON file to load
            
        Returns:
            The deserialized data
            
        Raises:
            FileOperationError: If the file cannot be read
            JSONSerializationError: If the file contains invalid JSON
        """
        try:
            with self.serialize(path, 'r') as file:
                self.data = json.load(file)
                return self.data
        except json.JSONDecodeError as e:
            raise JSONSerializationError(f"Failed to parse JSON from {path}: {str(e)}") from e