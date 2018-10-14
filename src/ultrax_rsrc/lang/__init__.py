import json as _json
import os as _os
import io as _io


def LoadJson(LanguageCode):

    dir_path = _os.path.dirname(_os.path.realpath(__file__))
    file_path = _os.path.join(dir_path, LanguageCode + ".JSON")

    if _os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return _json.load(f)
    else:
        raise FileNotFoundError()
