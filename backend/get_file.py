from collections import deque
from concurrent import futures
import hashlib
import pickle
import socket

from backend import constants
from backend.get_tracker_list import get_local_tracker_list
import requests


def get_file_info(fhash):
    tracker_ips = get_local_tracker_list()
    for tracker_ip in tracker_ips:
        try:
            r = requests.get(
                f"http://{tracker_ip}:{constants.TRACKER_PORT}/file_by_hash/{fhash}",
                timeout=constants.REQUEST_TIMEOUT,
            )
            r.raise_for_status()
            return r.json()
        except (requests.HTTPError, requests.ConnectionError, requests.Timeout, ValueError):
            continue

    return {
        "success": False,
        "error": "No trackers available",
    }


# Download the given file with the given number of threads
# It also takes a progress callback so it can update a progress bar every time a chunk is
# downloaded. It does NOT include the total number of chunks downloaded but instead calls
# the progress callback with True every time it succeeds to download a chunk, or False in
# two cases: either the chunk download has failed and should be aborted, or the download
# is complete.
# Returns a JSON object representing the result of the download, either success: True or
# success: False plus an error message.
def download_file(progress_callback, file_details_json):
    # Make sure the chunk directory exists
    constants.CHUNK_DOWNLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    # Return false if we failed to download the chunks
    download_result = download_many(file_details_json, progress_callback)
    if not download_result["success"]:
        return download_result

    # Download is complete
    progress_callback(False)

    # Combine the chunks and verify the file
    combine_chunks(file_details_json)
    verify_response = verify_full_file(file_details_json)
    if(verify_response["success"]):
        verify_response["name"] = file_details_json["name"]
        return verify_response
    else:
        return verify_response


# Verify the given full file
# Returns true on successful validation and false otherwise
def verify_full_file(file_details_json):
    file_name = file_details_json["name"]
    expected_hash = file_details_json["full_hash"]
    block_size = constants.BLOCK_SIZE
    sha256 = hashlib.sha256()

    with open(file_name, "rb") as f:
        buf = f.read(block_size)
        while len(buf) > 0:
            sha256.update(buf)
            buf = f.read(block_size)

    result = sha256.hexdigest() == expected_hash
    if result:
        return {"success": result}
    else:
        return {
            "success": result,
            "error": "Failed to validate full file hash",
        }


# Download the given file using the given number of threads
# Calls the given call back with True every time a chunk download succeeds, and False when
# a chunk download fails
# Returns True on successful download and False otherwise
def download_many(file_details_json, callback):
    chunks = file_details_json["chunks"]
    workers = min(constants.CHUNK_DOWNLOAD_THREADS, len(chunks))
    full_file_hash = file_details_json["full_hash"]
    peer_list = deque(file_details_json["peers"])

    with futures.ThreadPoolExecutor(max_workers=workers) as executor:
        res = []
        for chunk in chunks:
            future = executor.submit(download_one_chunk, full_file_hash, peer_list, callback, chunk)
            res.append(future)
            peer_list.rotate()

    if False in res:
        clean_chunks()
        return {
            "success": False,
            "error": "Failed to download file chunks",
        }
    else:
        return {"success": True}


# Combine the individual chunk files back into the original file
def combine_chunks(file_details_json):
    with open(file_details_json["name"], "wb") as full_file:
        for chunk in file_details_json["chunks"]:
            chunk_file = open(constants.CHUNK_DOWNLOAD_FOLDER / chunk["name"], "rb")
            chunk_data = chunk_file.read()
            chunk_file.close()
            (constants.CHUNK_DOWNLOAD_FOLDER / chunk["name"]).unlink()
            full_file.write(chunk_data)


# Clean the chunk directory of partial chunks or failed file download chunks
def clean_chunks():
    for chunk in constants.CHUNK_DOWNLOAD_FOLDER.iterdir():
        chunk.unlink()


# Attempt to download the given chunk from the list of peers and write the
# chunk to file. Call the callback with True if the chunk download succeeded, and False otherwise
# Returns True on success and False otherwise
def download_one_chunk(full_file_hash, peer_list, callback, chunk):
    request_data = {
        "full_hash": full_file_hash,
        "chunk_id": chunk["id"],
    }

    tries = 0
    while tries < constants.MAX_CHUNK_RETRY:
        for peer in peer_list:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect((peer["ip"], constants.PEER_PORT))
                except OSError:
                    # Try next peer if we can't connect
                    continue

                # Send the request
                s.sendall(pickle.dumps(request_data))

                # Recieve the file size (or -1 for error)
                chunk_size = pickle.loads(s.recv(64))

                # Try next peer if there was an error
                if chunk_size == -1:
                    continue

                # Recieve the file data
                chunk_data = recvall(s, chunk_size)

                # Check if we successfully recieved the data
                if chunk_data is None:
                    continue

                # Try the next peer if we can't verify the chunk
                if not verify_chunk(chunk_data, chunk["chunk_hash"]):
                    continue

                # Write the data to file
                with open(constants.CHUNK_DOWNLOAD_FOLDER / chunk["name"], "wb") as chunk_file:
                    chunk_file.write(chunk_data)

                callback(True)
                return True

        # If we failed to download a chunk, increment our tries counter
        tries += 1

    # Return false if we didn't successfully get the file from any peers
    callback(False)
    return False


# Verify the given chunk against the expected hash
# Returns true on successful verification, and false otherwise
def verify_chunk(chunk_data, expected_hash):
    actual_hash = hashlib.sha256(chunk_data).hexdigest()
    if expected_hash == actual_hash:
        return True
    else:
        return False


# Recieve n bytes from the given socket
# Returns the read bytes
def recvall(sock, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet

    return data
