import configparser
from pathlib import Path

CONFIG_FILE = Path.cwd() / "config.ini"
P2PFLIX_HEADER = "p2pflix"


# Reads config file, updates seq_number,
# writes guid if it does not exist
# and writes file
def update_seq(guid, seq_number):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    config.set(P2PFLIX_HEADER, "seq_number", str(seq_number+1))
    if "seq_number" not in config:
        config.set(P2PFLIX_HEADER, "guid", guid)
    with open(CONFIG_FILE, "w") as f:
        config.write(f)


# Reads the 'config.ini' to get configurations
# and returns them in a dict
# Creates a config file if one does not exit
def get_configs():
    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        return dict(config.items(P2PFLIX_HEADER))
    except Exception:
        return {
                "success": False,
                "error": "Error reading config file",
            }


# Creates a config.ini file and populates it
# with a seq_number
def add_seq():
    config = configparser.ConfigParser()
    config.add_section(P2PFLIX_HEADER)
    config.set(P2PFLIX_HEADER, "seq_number", "0")
    with open(CONFIG_FILE, "w") as f:
        config.write(f)
    return dict(config.items(P2PFLIX_HEADER))


# Remove the config file, resetting to default
def reset_config():
    try:
        CONFIG_FILE.unlink()
    except FileNotFoundError:
        # If the file doesn't exist, just return
        pass
