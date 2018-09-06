
from ._header import Header
from ._datatrack import DataTrack


class Mdx:
    '''A MDX performance data object.'''

    def __init__(self):
        self.Header = Header()
        self.Tones = []
        self.DataTracks = [DataTrack() for _ in range(16)]    # 16 channels
        #self.DataTracks = [bytearray() for _ in range(16)]    # 16 channels
        return


    def Export(self):
        '''Exports the current MDX object to a bytearray.'''
        e = bytearray(self.Header.Export() )

        for tone in self.Tones:
            e.extend(tone.Export() )

        for track in self.DataTracks:
            e.extend(track)

        return e
