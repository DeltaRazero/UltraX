import struct
from .encoding import *


class Header:
    '''MDX header object.'''
    def __init__(self):
        self.Title = ''
        self.PdxFilename = ''
        self.ToneDataOffset = 0
        self.SongDataOffsets = [0 for _ in range(16)]
        return

    def Export(self):
        '''Exports the current MDX header object to a bytearray.'''
        e = bytearray()
        for item in [self.Title.encode('shift-jis'), b"\x00\x0d\x0a\x10", self.PdxFilename.upper().encode()]:
            e.extend(item)

        if (self.PdxFilename[3:].upper() != ".PDX"):
            e.extend(".PDX".encode())
        e.extend(b"\x00")

        e.extend(struct.pack(ENC_WORD, self.ToneDataOffset))

        for item in self.SongDataOffsets:
            e.extend(struct.pack(ENC_WORD, item))

        return e
