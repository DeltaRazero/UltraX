
from . import dmf as dmfm
from ... import pymdx


class Channel_Data:

    Errors = None

    def Add(self, Command):
        self.Chunks[self.SeqPos].append(Command)

    def Extend(self, ListInpt):
        self.Chunks[self.SeqPos].extend(ListInpt)

    def Get(self, Position):
        return self.Chunks[self.SeqPos][Position]

    def Insert(self, Position, What):
        self.Chunks[self.SeqPos].insert(Position, What)

    def Advance(self):
        self.SeqPos += 1
        self.Seq.append(self.SeqPos)
        self.Chunks[self.SeqPos] = []
        return

    def __init__(self):
        self.SeqPos = 0
        self.Seq = []
        self.Chunks = {}
        self.Seq.append(self.SeqPos)
        self.Chunks[self.SeqPos] = []
        self.Errors = []
        return


    def Export(self):
        e = []
        for i in self.Seq:
            e += self.Chunks[i]
        return e


class Dmfc_Container:

    TIME_BASE : int = None
    REFRESH_RATE : int = None
    AMOUNT_CHANNELS : int = None

    USES_EXPCM : bool = False

    Channels : list = []

    DmfObj : dmfm = None
    MdxObj : pymdx.Mdx = None
    PdxObj : pymdx.Pdx = None


    def InitList(self):
        self.Channels = [Channel_Data() for _ in range(self.AMOUNT_CHANNELS)]


    def Export(self):

        for c, channel in enumerate(self.Channels):
            self.MdxObj.DataTracks[c].Extend(channel.Export() )
            del channel


def Set_MDX_Tone(ins) -> pymdx.Tone :
        """..."""
        tone = pymdx.Tone()

        tone.Alg = ins.Data.Alg
        tone.Fb = ins.Data.Fb

        for op in range(4):
            tone.Op[op].Ar = ins.Data.Op[op].Ar
            tone.Op[op].Dr = ins.Data.Op[op].Dr
            tone.Op[op].Sl = ins.Data.Op[op].Sl
            tone.Op[op].Sr = ins.Data.Op[op].Sr
            tone.Op[op].Rr = ins.Data.Op[op].Rr

            tone.Op[op].Tl = ins.Data.Op[op].Tl

            tone.Op[op].Dt1 = ins.Data.Op[op].Dt
            tone.Op[op].Dt2 = ins.Data.Op[op].Dt2

            tone.Op[op].Mult = ins.Data.Op[op].Mult

            tone.Op[op].Ks = ins.Data.Op[op].Ks

            tone.Op[op].Am_On = ins.Data.Op[op].Am

        return tone


class PcmInfo:
    Uses_Expcm = False
    Uses_Pcm = False

    def Analyse(self, dmf):
        for c in range(8, 12):
            for seq in dmf.Module.Channels[c].Sequence:
                for row in dmf.Module.Channels[c].Patterns[seq].Rows:
                    if (row.Note != 0 and row.Octave != 0):
                        if (c > 8):
                            self.Uses_Expcm = True
                        self.Uses_Pcm = True

                    for fx in row.Fx:
                        if (fx.Code != -1 or fx.Value != -1):
                            if (c > 8):
                                self.Uses_Expcm = True
        return

