"""
File utilities for APIpack.

This module provides file and directory manipulation utilities used throughout the application.
"""
import errno
import logging
import os
import shutil
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Union, cast

logger = logging.getLogger(__name__)

def ensure_directory(directory: Union[str, Path], mode: int = 0o755) -> Path:
    """Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory: Path to the directory.
        mode: Permissions to set on the directory (default: 0o755).
        
    Returns:
        Path object for the directory.
        
    Raises:
        OSError: If the directory cannot be created.
    """
    dir_path = Path(directory).expanduser().resolve()
    
    try:
        dir_path.mkdir(mode=mode, parents=True, exist_ok=True)
    except OSError as e:
        if e.errno != errno.EEXIST:  # Don't raise if directory already exists
            logger.error("Failed to create directory %s: %s", dir_path, e)
            raise
    
    # Ensure the directory has the correct permissions
    try:
        dir_path.chmod(mode)
    except OSError as e:
        logger.warning("Failed to set permissions on directory %s: %s", dir_path, e)
    
    return dir_path

def copy_file(
    src: Union[str, Path],
    dst: Union[str, Path],
    overwrite: bool = False,
    preserve_metadata: bool = True
) -> Path:
    """Copy a file from source to destination.
    
    Args:
        src: Source file path.
        dst: Destination file path.
        overwrite: Whether to overwrite the destination if it exists.
        preserve_metadata: Whether to preserve file metadata (timestamps, permissions).
        
    Returns:
        Path to the destination file.
        
    Raises:
        FileExistsError: If the destination exists and overwrite is False.
        OSError: If the file cannot be copied.
    """
    src_path = Path(src).expanduser().resolve()
    dst_path = Path(dst).expanduser()
    
    if not src_path.is_file():
        raise FileNotFoundError(f"Source file not found: {src_path}")
    
    if dst_path.exists() and not overwrite:
        raise FileExistsError(f"Destination file exists and overwrite=False: {dst_path}")
    
    # Ensure the destination directory exists
    ensure_directory(dst_path.parent)
    
    # Copy the file
    if preserve_metadata:
        shutil.copy2(str(src_path), str(dst_path))
    else:
        shutil.copy(str(src_path), str(dst_path))
    
    return dst_path.resolve()

def read_file(file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
    """Read the contents of a file.
    
    Args:
        file_path: Path to the file to read.
        encoding: File encoding (default: 'utf-8').
        
    Returns:
        The file contents as a string.
        
    Raises:
        FileNotFoundError: If the file does not exist.
        OSError: If the file cannot be read.
    """
    file_path = Path(file_path).expanduser().resolve()
    return file_path.read_text(encoding=encoding)

def write_file(
    file_path: Union[str, Path],
    content: str,
    encoding: str = 'utf-8',
    mode: str = 'w',
    ensure_parents: bool = True
) -> Path:
    """Write content to a file.
    
    Args:
        file_path: Path to the file to write.
        content: Content to write to the file.
        encoding: File encoding (default: 'utf-8').
        mode: File open mode (default: 'w' for write).
        ensure_parents: Whether to create parent directories if they don't exist.
        
    Returns:
        Path to the written file.
        
    Raises:
        OSError: If the file cannot be written.
    """
    file_path = Path(file_path).expanduser()
    
    if ensure_parents:
        ensure_directory(file_path.parent)
    
    file_path.write_text(content, encoding=encoding)
    return file_path.resolve()

def find_files(
    directory: Union[str, Path],
    pattern: str = '*',
    recursive: bool = True,
    include_dirs: bool = False,
    include_files: bool = True
) -> List[Path]:
    """Find files matching a pattern in a directory.
    
    Args:
        directory: Directory to search in.
        pattern: File pattern to match (e.g., '*.py').
        recursive: Whether to search recursively in subdirectories.
        include_dirs: Whether to include directories in the results.
        include_files: Whether to include files in the results.
        
    Returns:
        List of matching paths.
    """
    directory = Path(directory).expanduser().resolve()
    
    if not directory.is_dir():
        raise NotADirectoryError(f"Directory not found: {directory}")
    
    matches = []
    
    if recursive:
        for path in directory.rglob(pattern):
            if (include_files and path.is_file()) or (include_dirs and path.is_dir()):
                matches.append(path.relative_to(directory))
    else:
        for path in directory.glob(pattern):
            if (include_files and path.is_file()) or (include_dirs and path.is_dir()):
                matches.append(path.relative_to(directory))
    
    return sorted(matches)

def remove_file_or_dir(path: Union[str, Path], ignore_errors: bool = False) -> None:
    """Remove a file or directory.
    
    Args:
        path: Path to the file or directory to remove.
        ignore_errors: Whether to ignore errors if the path doesn't exist.
        
    Raises:
        OSError: If the path cannot be removed and ignore_errors is False.
    """
    path = Path(path).expanduser().resolve()
    
    try:
        if path.is_file() or path.is_symlink():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
        elif not ignore_errors:
            raise FileNotFoundError(f"Path not found: {path}")
    except FileNotFoundError:
        if not ignore_errors:
            raise

def is_empty_directory(directory: Union[str, Path]) -> bool:
    """Check if a directory is empty.
    
    Args:
        directory: Path to the directory.
        
    Returns:
        True if the directory is empty or doesn't exist, False otherwise.
    """
    directory = Path(directory).expanduser()
    
    if not directory.exists():
        return True
    
    if not directory.is_dir():
        return False
    
    return not any(directory.iterdir())

def get_file_hash(file_path: Union[str, Path], algorithm: str = 'sha256', chunk_size: int = 8192) -> str:
    """Calculate the hash of a file.
    
    Args:
        file_path: Path to the file.
        algorithm: Hash algorithm to use (default: 'sha256').
        chunk_size: Size of chunks to read from the file.
        
    Returns:
        The file's hash as a hexadecimal string.
        
    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the algorithm is not available.
    """
    import hashlib
    
    file_path = Path(file_path).expanduser().resolve()
    
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        hash_func = getattr(hashlib, algorithm)()
    except AttributeError:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()

def create_temp_file(
    content: str = '',
    suffix: str = '',
    prefix: str = 'tmp',
    dir: Optional[Union[str, Path]] = None,
    delete: bool = True,
    encoding: str = 'utf-8'
) -> Path:
    """Create a temporary file with the given content.
    
    Args:
        content: Initial content to write to the file.
        suffix: File suffix (e.g., '.txt').
        prefix: File prefix (default: 'tmp').
        dir: Directory to create the file in. If None, uses the system temp dir.
        delete: Whether to delete the file when closed.
        encoding: File encoding (default: 'utf-8').
        
    Returns:
        Path to the created temporary file.
    """
    import tempfile
    
    mode = 'w+' if content else 'w'
    
    with tempfile.NamedTemporaryFile(
        mode=mode,
        suffix=suffix,
        prefix=prefix,
        dir=str(dir) if dir else None,
        delete=delete,
        encoding=encoding
    ) as f:
        if content:
            f.write(content)
            f.flush()
        
        # On Windows, we need to close the file before we can use it
        temp_path = Path(f.name)
        
        if not delete:
            # On Unix, we can keep the file open
            f._closer.delete = False
            return temp_path.resolve()
    
    # On Windows, we need to reopen the file
    if not delete:
        return temp_path.resolve()
    
    # Shouldn't get here if delete=True, as the file would be deleted
    raise RuntimeError("Failed to create temporary file")
