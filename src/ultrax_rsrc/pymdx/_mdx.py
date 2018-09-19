from ._header import Header
from ._datatrack import Datatrack


class Mdx:
    '''A MDX performance data object.'''

    def __init__(self):
        self.Header = Header()
        self.Tones = []
        self.DataTracks = [Datatrack() for _ in range(16)]    # 16 channels
        #self.DataTracks = [bytearray() for _ in range(16)]    # 16 channels
        return


    def Export(self):
        '''Exports the current MDX object to a bytearray.'''

        tonedata = bytearray()
        [tonedata.extend(b) for b in 
            [tone._Export() for tone in self.Tones]
        ]

        trackdata = bytearray()
        for c, b in enumerate([track._Export() for track in self.DataTracks]):
            trackdata.extend(b)
            self.Header._SongDataOffsets[c] = len(b)

        # Export
        e = bytearray(self.Header._Export() )
        e.extend(tonedata)
        e.extend(trackdata)

        return e
