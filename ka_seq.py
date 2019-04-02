from pathlib import Path
import pickle

KA_SEQ_FILE = "./ka_seq.dat"


# Make sure the keep alive sequence number file exists
# Returns a Path object pointing to the file
def check_ka_file():
    ka_file_path = Path(KA_SEQ_FILE)

    if not ka_file_path.is_file():
        with open(ka_file_path, "wb") as fd:
            pickle.dump(0, fd)

    return ka_file_path


# Get the current keep alive sequence number
def get_ka_seq():
    ka_path = check_ka_file()

    with open(ka_path, "rb") as fd:
        return pickle.load(fd)


# Increment the keep alive sequence number
# Returns the pre-increment sequence number
def increment_ka_seq():
    ka_path = check_ka_file()

    with open(ka_path, "r+b") as fd:
        num = pickle.load(ka_path)
        fd.seek(0)
        pickle.dump(num + 1, ka_path)

    return num


# Set the keep alive sequence number to the given value
def set_ka_seq(new_val):
    ka_path = check_ka_file()

    with open(ka_path, "wb") as fd:
        pickle.dump(new_val, fd)
