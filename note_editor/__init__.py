"""Top-level package for note-editor."""

import configparser
import os
path = os.path.dirname(os.path.abspath(__file__))

__author__ = """Chloé dh"""
__email__ = 'chloe_dh@riseup.net'
__version__ = '0.1.0'

if not os.path.exists(os.path.join(path, "config.ini")):
    # create config file to store previous pdf locations
    config = configparser.ConfigParser()
    config.add_section('save_path')
    config['save_path']['head'] = "~"
    config['save_path']['tail'] = 'notes_on_stuff.pdf'
    with open(os.path.join(path, "config.ini"), 'w') as f:
        config.write(f)

