from pathlib import Path

TRACKER_PORT = 42070  # Default tracker port
PEER_PORT = 65432  # Default peer listen port
REQUEST_TIMEOUT = 5  # Default timeout for a tracker request in seconds
LISTEN_IP = "0.0.0.0"  # Seeder should listen on all interfaces by default
CHUNK_DOWNLOAD_FOLDER = Path.cwd() / ".chunks"  # location of temporary downloading chunks
CHUNK_DOWNLOAD_THREADS = 1  # How many threads to download files with
KEEPALIVE_TIME = 5  # Keepalive interval in seconds
CHUNK_DIRECTORY = Path.cwd() / "files"  # Default chunk download
CHUNK_SIZE = 10000000  # Size of the chunks
BLOCK_SIZE = 4096  # Block size for hashing iteratively
MAX_CHUNK_RETRY = 3  # How many times to try downloading a chunk from the list of peers
