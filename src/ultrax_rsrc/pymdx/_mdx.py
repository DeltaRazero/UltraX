from ._header import Header
from ._datatrack import Datatrack


class Mdx:
    """A MDX performance data object."""

    def __init__(self, ExPcm=False):
        self.Header = Header(ExPcm)
        self.Tones = []
        self.DataTracks = [Datatrack() for _ in range(16 if ExPcm else 9)]    # 16 channels
        return


    def Export(self):
        '''Exports the current MDX object to a bytearray.'''

        tonedata = bytearray()
        [tonedata.extend(t) for t in 
            [tone._Export() for tone in self.Tones]
        ]

        #self.Header._ToneDataOffset = 2 * len(self.DataTracks)

        trackdata = [bytearray() for _ in range(len(self.DataTracks))]
        for c, track in enumerate(self.DataTracks):
            if (True):
                track.Add.DataEnd(track.Add._lm)
            trackdata[c].extend(track._Export())
            if (c>0):
                self.Header._SongDataOffsets[c] = len(trackdata[c-1]) + self.Header._SongDataOffsets[c-1]
            else:
                self.Header._SongDataOffsets[c] = 2 + 2 * len(self.DataTracks)

        self.Header._ToneDataOffset = 2 + 2 * len(self.DataTracks)
        for track in trackdata:
            self.Header._ToneDataOffset += len(track)

        # Export
        e = bytearray(self.Header._Export())
        for track in trackdata:
            e.extend(track)
        e.extend(tonedata)

        return e
