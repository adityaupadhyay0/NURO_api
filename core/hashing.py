import hashlib

def calculate_file_hash(file_path: str) -> str:
    """Calculates the SHA-256 hash of a file for caching and deduplication."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read file in chunks to handle large files efficiently
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
