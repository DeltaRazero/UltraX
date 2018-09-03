
class Header:
    '''MDX header object.'''
    def __init__(self):
        self.Title = bytearray(b"\x00\x0d\x0a\x10")
        self.PdxFilename = bytearray(b"\x00")
        self.ToneDataOffset = 0
        self.SongDataOffset = 0
        return

    def SetTitle(self, Title):
        self.Title = bytearray(Title, 'shift-jis')
        self.Title.append(b"\x00\x0d\x0a\x10")
        return

    def SetPdxFilename(self, PdxFilename):
        self.PdxFilename = bytearray(PdxFilename)
        # TODO: Check for file extension
        self.PdxFilename.append(b"\x00")
        return

    def Export(self):
        '''Exports the current MDX header object to a bytearray.'''
        return bytearray([self.Title, self.PdxFilename, self.ToneDataOffset, self.SongDataOffset])
