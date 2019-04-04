from pathlib import Path
import shutil

from backend import constants, ka_seq
from backend.deregister_file_by_hash import deregister_file
from backend.get_configs import get_configs, update_seq
from backend.get_peer_status import get_status


def resolve():
    # Get our status from the tracker
    status = get_status()

    # Get current and expected seq_number
    configs = get_configs()
    expected_seq = status["expected_seq_number"]
    update_seq(configs["guid"], expected_seq - 1)

    expected_ka_seq = status["ka_expected_seq_number"]
    ka_seq.set_ka_seq(expected_ka_seq - 1)

    # Get tracker and peer file lists
    tracker_list = [f["full_hash"] for f in status["files"]]
    peer_list = list((Path.cwd() / ("files")).iterdir())

    # Remove files from tracker that the peer doesn't have
    for fhash in tracker_list:
        if fhash in peer_list:
            peer_list.remove(fhash)
        else:
            deregister_file(fhash)

    # Remove files from peer the tracker doesn't have
    failures = []
    for fpeer in peer_list:
        if fpeer not in tracker_list:
            try:
                shutil.rmtree(constants.CHUNK_DIRECTORY / fpeer)
            except OSError:
                failures.append(fpeer)

    if failures:
        return {
            "success": False,
            "error": f"Failed to remove the following files: {', '.join(failures)}",
        }

    return {"success": True}
