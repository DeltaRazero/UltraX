from ._datatrack import Datatrack
from ._header import Header


class Mdx:
    """A MDX performance data object."""

    def __init__(self, Expcm=False):
        c = 16 if Expcm else 9  # Amount of tracks
        self.Header = Header(c)
        self.Tones = []
        self.DataTracks = [Datatrack() for _ in range(c)]
        if Expcm:
            self.DataTracks[0].Add.Expcm_Enable()
        return

    def Export(self):
        '''Exports the current MDX object to a bytearray.'''

        tonedata = bytearray()
        for t in [tone._Export() for tone in self.Tones]:
            tonedata.extend(t)

        d = [bytearray() for _ in range(len(self.DataTracks))]
        for c, track in enumerate(self.DataTracks):
            d[c].extend(track._Export())
            if (c > 0):
                self.Header._SongDataOffsets[c] = len(d[c-1]) + self.Header._SongDataOffsets[c-1]
            else:
                self.Header._SongDataOffsets[c] = 2 + 2 * len(self.DataTracks)

        self.Header._ToneDataOffset = 2 + 2 * len(self.DataTracks)
        for track in d:
            self.Header._ToneDataOffset += len(track)

        # Export
        e = bytearray(self.Header._Export())
        for track in d:
            e.extend(track)
        e.extend(tonedata)

        return e
