import json as _json
import os as _os
import io as _io


# Global variable containing the JSON data
JSON_DATA = None

def LoadJson(LanguageCode):
    """Load JSON data into variable `JSON_DATA`, with corrosponding language code (see directory `.JSON` file names)."""
    global JSON_DATA

    dir_path = _os.path.dirname(_os.path.realpath(__file__))
    file_path = _os.path.join(dir_path, LanguageCode + ".JSON")

    if _os.path.exists(file_path):
        with _io.StringIO(open(file_path, 'r').read()) as f:
            JSON_DATA = _json.load(f)
    else:
        raise FileNotFoundError('The JSON file "{}" could not be opened (does it exist?).'.format(file_path))
