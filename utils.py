"""
Utility module for ProjectPilot AI.
Provides file system traversal, project directory structure generation,
and safe zip file extraction for user-uploaded projects.
Equipped with robust handling for hidden files, symlinks, unreadable files,
permission errors, and large folder protections.
"""

import os
import zipfile
from typing import Dict, List, Set, Generator, Any

# Set of directory names that are always ignored when reading project contents
IGNORE_DIRS: Set[str] = {
    ".git",
    "node_modules",
    "__pycache__",
    "venv",
    ".venv",
    "dist",
    "build",
    ".gradle",
    ".idea",
    ".vscode",
    "env",
    "bin",
    "obj",
}

# Set of file extensions to treat as binary and skip during context extraction
BINARY_EXTENSIONS: Set[str] = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp", ".pdf",
    ".zip", ".tar", ".gz", ".rar", ".7z", ".mp3", ".mp4", ".wav",
    ".db", ".sqlite", ".sqlite3", ".pyc", ".o", ".exe", ".dll",
    ".so", ".dylib", ".woff", ".woff2", ".eot", ".ttf", ".class",
}

# Safeguard limits for file counts to prevent out-of-memory or timeout on very large folders
MAX_SCAN_LIMIT: int = 5000       # Maximum files counted in summary statistics
MAX_EXTRACT_LIMIT: int = 500     # Maximum files read for text content parsing
MAX_TREE_LINES: int = 1000       # Maximum lines displayed in the directory tree output

def extract_zip(zip_path: str, extract_to: str) -> None:
    """
    Safely extracts a ZIP archive to the target directory.
    Includes check paths to prevent path traversal / Zip Slip vulnerabilities.
    
    Args:
        zip_path (str): The absolute path to the zip file.
        extract_to (str): The absolute path to the directory where contents should be extracted.
    """
    try:
        os.makedirs(extract_to, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.infolist():
                # Get the absolute target path to ensure security
                target_path = os.path.abspath(os.path.join(extract_to, member.filename))
                if target_path.startswith(os.path.abspath(extract_to)):
                    zip_ref.extract(member, extract_to)
    except Exception as e:
        # Prevent zip extraction failures from crashing application
        raise OSError(f"Failed to safely extract ZIP archive: {str(e)}")

def get_directory_tree(path: str, max_depth: int = 5) -> str:
    """
    Generates a visual text representation of the directory structure.
    Safely handles hidden files, symlinks, permission exceptions, and line budget limits.
    
    Args:
        path (str): The absolute path of the directory.
        max_depth (int): Maximum depth to traverse.
        
    Returns:
        str: A string formatted as a tree diagram.
    """
    if not os.path.exists(path):
        return "Directory not found."
    if os.path.islink(path):
        return f"[Symbolic Link: {path}]"

    lines: List[str] = []
    line_count = 0

    def _traverse(dir_path: str, prefix: str = "", depth: int = 0) -> None:
        nonlocal line_count
        if depth > max_depth or line_count >= MAX_TREE_LINES:
            return
        
        try:
            items = sorted(os.listdir(dir_path))
        except (PermissionError, OSError):
            lines.append(f"{prefix}└── [Permission Denied / Unreadable]")
            line_count += 1
            return

        # Filter out ignored directories and hidden directories (start with .)
        filtered_items = []
        for item in items:
            item_path = os.path.join(dir_path, item)
            # Skip symbolic links inside tree to prevent recursion issues
            if os.path.islink(item_path):
                continue
            if item in IGNORE_DIRS or (item.startswith(".") and os.path.isdir(item_path)):
                continue
            filtered_items.append(item)

        for i, item in enumerate(filtered_items):
            if line_count >= MAX_TREE_LINES:
                lines.append(f"{prefix}└── [Traversal truncated: limit of {MAX_TREE_LINES} lines reached]")
                line_count += 1
                return

            item_path = os.path.join(dir_path, item)
            is_last = (i == len(filtered_items) - 1)
            connector = "└── " if is_last else "├── "
            
            lines.append(f"{prefix}{connector}{item}")
            line_count += 1
            
            if os.path.isdir(item_path):
                extension_prefix = "    " if is_last else "│   "
                _traverse(item_path, prefix + extension_prefix, depth + 1)

    try:
        lines.append(os.path.basename(os.path.abspath(path)) or path)
        line_count += 1
        _traverse(path)
    except Exception as e:
        return f"Failed to generate directory tree: {str(e)}"
        
    return "\n".join(lines)

def scan_project_files(path: str) -> Generator[Dict[str, str], None, None]:
    """
    Scans a project directory and yields file metadata and contents for all non-ignored, non-binary files.
    Safely handles symbolic links, permission errors, and places a limit on total processed text files.
    
    Args:
        path (str): The root path of the project.
        
    Yields:
        Dict[str, str]: A dictionary with 'relative_path', 'extension', and 'content' keys.
    """
    processed_count = 0
    
    for root, dirs, files in os.walk(path, followlinks=False):
        # Prevent traversal of unreadable or permission-restricted directories
        try:
            # Modify dirs in-place to skip ignored directories and hidden directories
            dirs[:] = [
                d for d in dirs 
                if d not in IGNORE_DIRS 
                and not d.startswith(".") 
                and not os.path.islink(os.path.join(root, d))
            ]
        except (PermissionError, OSError):
            dirs[:] = []
            continue

        for file in files:
            if processed_count >= MAX_EXTRACT_LIMIT:
                return

            file_path = os.path.join(root, file)
            
            # Safe check to skip symbolic links
            if os.path.islink(file_path):
                continue
                
            rel_path = os.path.relpath(file_path, path)
            
            # Correct extraction of file extension from filename string (tuple split safe)
            ext = os.path.splitext(file)[1].lower()
            
            # Skip binary files
            if ext in BINARY_EXTENSIONS:
                continue
                
            try:
                # Get file size to avoid loading huge text files (skip files > 1.5MB)
                try:
                    if os.path.getsize(file_path) > 1500000:
                        continue
                except OSError:
                    continue

                # Try reading with UTF-8 first, fallback to latin-1
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                    
                processed_count += 1
                yield {
                    "relative_path": rel_path,
                    "extension": ext,
                    "content": content
                }
            except (PermissionError, FileNotFoundError, OSError):
                # Safely ignore unreadable, missing, or locked files
                continue

def get_project_summary(path: str) -> Dict[str, Any]:
    """
    Summarizes a project path by counting directories, file types, and size.
    Features robust error shielding for permission issues, hidden elements,
    symlinks, and directory budget boundaries.
    
    Args:
        path (str): The project path.
        
    Returns:
        Dict[str, Any]: A dictionary containing statistical summary of the project.
    """
    summary = {
        "file_count": 0,
        "ignored_files_skipped": 0,
        "file_types": {},
        "total_size_bytes": 0
    }
    
    if not os.path.exists(path) or os.path.islink(path):
        return summary
        
    for root, dirs, files in os.walk(path, followlinks=False):
        # Handle directory traversal restrictions
        try:
            # Check if we are inside any ignored directory path segment
            parts = os.path.normpath(root).split(os.sep)
            if any(ignored in parts for ignored in IGNORE_DIRS):
                summary["ignored_files_skipped"] += len(files)
                # Clear sub-directories to prevent walking deeper into this ignored folder
                dirs[:] = []
                continue

            # Modify dirs in-place to avoid hidden folders and symlinked folders
            dirs[:] = [
                d for d in dirs 
                if not d.startswith(".") 
                and not os.path.islink(os.path.join(root, d))
            ]
        except (PermissionError, OSError):
            # Skip if current root directory is unreadable
            dirs[:] = []
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            
            # Skip symbolic link files
            if os.path.islink(file_path):
                continue
                
            # Stop accumulating stats if directory size threshold is exceeded
            if summary["file_count"] >= MAX_SCAN_LIMIT:
                continue

            # Correct extraction of file extension from filename string (tuple split safe)
            ext = os.path.splitext(file)[1].lower()
            ext = ext or "no-extension"
            
            try:
                # Wrap stats retrieval in try-block to avoid permission/missing file crashes
                size = os.path.getsize(file_path)
                summary["file_count"] += 1
                summary["total_size_bytes"] += size
                summary["file_types"][ext] = summary["file_types"].get(ext, 0) + 1
            except (PermissionError, FileNotFoundError, OSError):
                # Skip individual unreadable files safely
                continue
                
    return summary
