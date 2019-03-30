import configparser


# Reads config file, updates seq_number,
# writes guid if it does not exist
# and writes file
def update_seq(guid, seq_number):
    config = configparser.ConfigParser()
    config.read('config.ini')
    config.set('p2pflix', 'seq_number', str(seq_number+1))
    if 'seq_number' not in config:
        config.set('p2pflix', 'guid', guid)
    with open('config.ini', 'w') as f:
        config.write(f)


# Reads the 'config.ini' to get configurations
# and returns them in a dict
# Creates a config file if one does not exit
def get_configs():
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')
        return dict(config.items('p2pflix'))
    except Exception:
        print('error with config.ini')


# Creates a config.ini file and populates it
# with a seq_number
def add_seq():
    config = configparser.ConfigParser()
    config.add_section('p2pflix')
    config.set('p2pflix', 'seq_number', '0')
    with open('config.ini', 'w') as f:
        config.write(f)
    return dict(config.items('p2pflix'))
