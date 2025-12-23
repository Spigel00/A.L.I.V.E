"""
File Tools

Filesystem utilities for agent operations.
UTF-8 encoding, no silent failures, no caching.
"""

import os
from pathlib import Path


def read_file(path: str) -> str:
    """
    Read file contents.
    
    Args:
        path: Absolute or relative file path
        
    Returns:
        File contents as string
        
    Raises:
        FileNotFoundError: If file does not exist
        IOError: If read fails
    """
    file_path = Path(path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(path: str, content: str):
    """
    Write content to file.
    
    Args:
        path: Absolute or relative file path
        content: Content to write
        
    Raises:
        IOError: If write fails
    """
    file_path = Path(path)
    
    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def delete_file(path: str):
    """
    Delete a file.
    
    Args:
        path: Absolute or relative file path
        
    Raises:
        FileNotFoundError: If file does not exist
        IOError: If deletion fails
    """
    file_path = Path(path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    file_path.unlink()
