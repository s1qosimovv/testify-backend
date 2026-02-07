"""
Helper utility functions
"""

def truncate_text(text: str, max_length: int = 3000) -> str:
    """Truncate text to maximum length"""
    return text[:max_length] if len(text) > max_length else text

def validate_file_extension(filename: str, allowed_extensions: set) -> bool:
    """Check if file extension is allowed"""
    return any(filename.lower().endswith(ext) for ext in allowed_extensions)
