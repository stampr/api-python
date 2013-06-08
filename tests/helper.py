from __future__ import absolute_import, unicode_literals, print_function, division

import os
import json
import sys

def json_data(name):
    '''Load json data from a file in the data/ folder and parse it'''
    
    return json.loads(json_str(name))

def json_str(name):
    '''Load raw json string from a file in the data/ folder'''
    
    path = os.path.join(os.path.dirname(__file__), "data/%s.json" % name)
    with open(path) as f:
        return f.read()

def to_bytes(str):
    if sys.version_info[0] < 3:
        return bytes(str)
    else:
        return bytes(str, "ascii")