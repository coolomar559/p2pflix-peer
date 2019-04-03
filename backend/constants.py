from pathlib import Path

TRACKER_PORT = 42069  # Default tracker port is 42069
PEER_PORT = 65432  # Default peer listen port is 65432
REQUEST_TIMEOUT = 30  # Default timeout for a tracker request is 30 seconds
LISTEN_IP = '0.0.0.0'  # Seeder should listen on all interfaces by default
CHUNK_DOWNLOAD_FOLDER = Path.cwd() / ".chunks"  # location of temporary downloading chunks
KEEPALIVE_TIME = 60  # Keepalive every 60 seconds
CHUNK_DIRECTORY = Path.cwd() / 'files'  # Default storing chunks for seeding to ./files/
CHUNK_SIZE = 10000000  # Size of the chunks
BLOCK_SIZE = 4096  # Block size for hashing iteratively
MAX_CHUNK_RETRY = 3  # How many times to try downloading a chunk from the list of peers
