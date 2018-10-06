import struct as struct
from ._encoding import *


class Header:
    """MDX header object."""
    
    def __init__(self, TrackCount):
        self.Title = ""
        self.PdxFilename = ""
        self._ToneDataOffset = 0
        self._SongDataOffsets = [0 for _ in range(TrackCount)]
        return

    def _Export(self):
        '''Exports the current MDX header object to a bytearray.'''
        e = bytearray()
        for item in [self.Title.encode('shift-jis'), b"\x0d\x0a\x1a", self.PdxFilename.upper().encode()]:
            e.extend(item)

        if (self.PdxFilename != ''  and  self.PdxFilename[-4:].upper() != ".PDX"):
            e.extend(".PDX".encode())
        e.extend(b"\x00")

        e.extend(struct.pack(ENC_WORD, self._ToneDataOffset))

        for item in self._SongDataOffsets:
            e.extend(struct.pack(ENC_WORD, item))

        return e
